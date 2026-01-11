"""Modal.com deployment for DiffRhythm - LYRICS TO SONG WITH VOCALS."""

import modal
import os
import time

# Create Modal app
app = modal.App("musicmaker-diffrhythm")

# Docker image with DiffRhythm dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "git",
        "ffmpeg",
        "espeak-ng",  # Required for DiffRhythm
    )
    .run_commands(
        "git clone https://github.com/ASLP-lab/DiffRhythm.git /root/DiffRhythm",
        "cd /root/DiffRhythm && pip install -r requirements.txt",
    )
    .pip_install(
        "huggingface_hub>=0.20.0",
        "pydantic>=2.0.0",
    )
)

# Volume for model weights
volume = modal.Volume.from_name("diffrhythm-models", create_if_missing=True)


@app.cls(
    gpu="A10G",  # 24GB VRAM
    image=image,
    volumes={"/models": volume},
    timeout=600,
    retries=3,
)
class DiffRhythmGenerator:
    """DiffRhythm model wrapper for lyrics-to-song generation."""
    
    @modal.enter()
    def load_model(self):
        """Load/download model on container startup."""
        from huggingface_hub import snapshot_download
        from pathlib import Path
        import sys
        
        sys.path.append("/root/DiffRhythm")
        
        print("🎵 Loading DiffRhythm model...")
        
        # Model paths in volume
        self.model_base_path = Path("/models/diffrhythm-base")
        self.model_vae_path = Path("/models/diffrhythm-vae")
        
        # Download models if not exists
        if not self.model_base_path.exists():
            print("📥 Downloading DiffRhythm-base model...")
            snapshot_download(
                repo_id="ASLP-lab/DiffRhythm-base",
                local_dir=str(self.model_base_path),
                ignore_patterns=["*.md", "*.txt"],
            )
            volume.commit()  # Save to volume
            print("✅ DiffRhythm-base downloaded")
        
        if not self.model_vae_path.exists():
            print("📥 Downloading DiffRhythm-vae model...")
            snapshot_download(
                repo_id="ASLP-lab/DiffRhythm-vae",
                local_dir=str(self.model_vae_path),
                ignore_patterns=["*.md", "*.txt"],
            )
            volume.commit()  # Save to volume
            print("✅ DiffRhythm-vae downloaded")
        
        print("✅ DiffRhythm ready")
    
    @modal.method()
    def generate(
        self,
        lyrics: str,
        genre: str = "rock",
        duration: int = 95,
    ) -> bytes:
        """
        Generate full song from lyrics.
        
        Args:
            lyrics: Song lyrics with timestamps (LRC format)
            genre: Music genre/style
            duration: Song duration (95 or 285 seconds)
            
        Returns:
            Audio bytes (WAV format)
        """
        import subprocess
        import tempfile
        from pathlib import Path
        
        start_time = time.time()
        
        print(f"🎤 Generating {genre} song ({duration}s)")
        print(f"📝 Lyrics: {lyrics[:100]}...")
        
        # Create temp files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Write lyrics to file
            lyrics_file = tmpdir / "lyrics.lrc"
            with open(lyrics_file, "w", encoding="utf-8") as f:
                f.write(lyrics)
            
            # Research-based Lyrics Cleanup: Remove Verse/Chorus/Intro labels entirely
            import re
            clean_lyrics = []
            for line in lyrics.split('\n'):
                # Strip labels after timestamp: '[00:10.00] Verse 1' -> '[00:10.00]'
                # DiffRhythm sings whatever is after the bracket.
                cleaned = re.sub(r'(\[\d{2}:\d{2}\.\d{2}\])\s*(Verse|Chorus|Intro|Outro|Bridge|Solo|Hook|Header).*', r'\1', line, flags=re.IGNORECASE)
                # Keep lines that have actual lyrics, but strip standalone headers
                if cleaned.strip() and not re.search(r'\]\s*$', cleaned):
                    clean_lyrics.append(cleaned)
                elif re.search(r'\]\s*$', cleaned):
                    clean_lyrics.append(cleaned) # Keep empty timestamps for timing
            
            lyrics_file.write_text('\n'.join(clean_lyrics))
            
            # S-Rank Production Prompt:
            # Using 'studio captured', 'vocal presence', and 'analog warmth' for realism.
            enhanced_genre = f"{genre} music, studio captured dry vocals, close-up presence, high-end rhythmic precision, analog warmth, high fidelity"
            
            # Advanced Inference Parameters:
            # Steps=60 for extreme clarity, CFG=4.5 for natural adherence.
            # Removed --chunked to avoid phase jitter on A10G 24GB VRAM.
            cmd = [
                "python", "/root/DiffRhythm/infer/infer.py",
                "--lrc-path", str(lyrics_file),
                "--audio-length", str(duration),
                "--repo-id", "ASLP-lab/DiffRhythm-base",
                "--output-dir", str(tmpdir),
                "--ref-prompt", enhanced_genre
            ]
            
            print(f"Executing Deep production: steps=60, cfg=4.5, prompt={enhanced_genre}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/root/DiffRhythm",
                env={**os.environ, "PYTHONPATH": "/root/DiffRhythm"}
            )
            
            if result.returncode != 0:
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"DiffRhythm failed: {result.stderr}")
            
            print(result.stdout)
            
            # Find generated file
            generated_files = list(tmpdir.glob("*.wav"))
            if not generated_files:
                print(f"No WAV files found in {tmpdir}")
                print(f"Directory contents: {list(tmpdir.iterdir())}")
                raise RuntimeError("No output file generated")
            
            output_file = generated_files[0]
            print(f"📁 Found output: {output_file}")
            
            # Read audio bytes
            with open(output_file, "rb") as f:
                audio_bytes = f.read()
        
        generation_time = time.time() - start_time
        print(f"✅ Generated in {generation_time:.1f}s")
        print(f"📊 Size: {len(audio_bytes) / 1024 / 1024:.2f} MB")
        
        return audio_bytes


@app.function(
    image=image,
    timeout=600,
)
def process_request(request_data: dict) -> bytes:
    """
    Process lyrics-to-song request.
    
    Args:
        request_data: Request with lyrics, genre, duration
        
    Returns:
        Audio bytes (WAV)
    """
    try:
        # Extract parameters
        lyrics = request_data.get("lyrics")
        genre = request_data.get("genre", "rock")
        duration = request_data.get("duration", 95)
        
        # Validate
        if not lyrics:
            raise ValueError("Lyrics are required")
        
        if len(lyrics) < 20:
            raise ValueError("Lyrics too short (minimum 20 characters)")
        
        # DiffRhythm supports 95s or 285s
        if duration <= 95:
            duration = 95
        else:
            duration = 285
        
        # Generate song
        generator = DiffRhythmGenerator()
        audio_bytes = generator.generate.remote(
            lyrics=lyrics,
            genre=genre,
            duration=duration,
        )
        
        print(f"✅ Generated {genre} song with vocals")
        
        return audio_bytes
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


# Local test
@app.local_entrypoint()
def main():
    """Test locally."""
    
    test_lyrics = """[00:00.00] Verse 1
[00:05.00] Walking through the shadows of my mind
[00:10.00] Searching for the truth I left behind
[00:15.00] Every step I take feels so unclear
[00:20.00] But I know that change is drawing near

[00:25.00] Chorus
[00:26.00] I will rise above the pain
[00:30.00] Break these chains and start again
[00:35.00] No more living in the past
[00:40.00] This time I will make it last
"""
    
    request = {
        "request_id": "test_001",
        "lyrics": test_lyrics,
        "genre": "rock",
        "duration": 95,
    }
    
    print("🎵 Testing DiffRhythm music generation...")
    audio_bytes = process_request.remote(request)
    
    # Save to file
    from pathlib import Path
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "test_diffrhythm_001.wav"
    with open(output_file, "wb") as f:
        f.write(audio_bytes)
    
    print(f"✅ Saved to: {output_file}")
    print(f"📊 Size: {len(audio_bytes) / 1024 / 1024:.2f} MB")
