"""Modal.com deployment for DiffRhythm - LYRICS TO SONG WITH VOCALS."""

import modal
import os
import time
import re

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
        
        # Create temp files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            lyrics_file = tmpdir / "lyrics.lrc"
            
            # Clean lyrics for DiffRhythm (No Verse/Chorus text, No Empty lines)
            clean_lyrics = []
            for line in lyrics.split('\n'):
                # 1. Strip structural labels: '[00:10.00] Verse 1' -> '[00:10.00]'
                line = re.sub(r'(\[\d{2}:\d{2}\.\d{2}\])\s*(Verse|Chorus|Intro|Outro|Bridge|Solo|Hook|Header).*', r'\1', line, flags=re.IGNORECASE)
                
                # 2. Only keep lines with actual text to prevent 'Unknown Language' error
                # Forced space after ] is critical for DiffRhythm's tokenizer
                if re.search(r'\]\s*\S+', line):
                    # Ensure single space after bracket ]
                    line = re.sub(r'\]\s*', r'] ', line)
                    clean_lyrics.append(line.strip())
            
            final_lrc = '\n'.join(clean_lyrics)
            lyrics_file.write_text(final_lrc)
            
            print(f"📝 Processed LRC ({len(clean_lyrics)} lines)")
            
            # Stable High-Quality Settings
            enhanced_genre = f"{genre}, studio recording, clear dry vocals, steady rhythm, high fidelity"
            cmd = [
                "python3", "/root/DiffRhythm/infer/infer.py",
                "--lrc-path", str(lyrics_file),
                "--audio-length", str(duration),
                "--output-dir", str(tmpdir),
                "--ref-prompt", enhanced_genre,
                "--chunked"
            ]
            
            print(f"Executing DiffRhythm production...")
            
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
            
            # Find generated file
            generated_files = list(tmpdir.glob("*.wav"))
            if not generated_files:
                raise RuntimeError("No output file generated")
            
            output_file = generated_files[0]
            with open(output_file, "rb") as f:
                audio_bytes = f.read()
        
        generation_time = time.time() - start_time
        print(f"✅ Generated in {generation_time:.1f}s (Size: {len(audio_bytes)/1024/1024:.2f} MB)")
        return audio_bytes


def get_lyrics_from_data(data: dict) -> str:
    """Helper to extract lyrics from either 'lyrics' or 'structure' field."""
    lyrics_text = data.get("lyrics", "")
    structure = data.get("structure", [])
    
    if structure:
        lrc_lines = []
        for section in structure:
            start_str = section.get("start", "00:00.00")
            time_match = re.search(r'(\d{2}):(\d{2}\.\d{2})', start_str)
            
            if time_match:
                base_min = int(time_match.group(1))
                base_sec = float(time_match.group(2))
                base_total = base_min * 60 + base_sec
                
                lines = section.get("lines", [])
                for i, line in enumerate(lines):
                    # Auto-distribute lines with 4s gap
                    line_total = base_total + (i * 4.0)
                    m = int(line_total // 60)
                    s = line_total % 60
                    ts = f"[{m:02d}:{s:05.2f}] "
                    lrc_lines.append(f"{ts}{line.strip()}")
        return "\n".join(lrc_lines)
    return lyrics_text


@app.function(image=image, timeout=600)
def process_request(request_data: dict) -> bytes:
    """Process lyrics-to-song request."""
    try:
        # Extract and convert lyrics
        lyrics = get_lyrics_from_data(request_data)
        genre = request_data.get("genre", "rock")
        duration = request_data.get("duration", 95)
        
        if not lyrics:
            raise ValueError("No lyrics or structure provided")
        
        # Duration normalization
        duration = 285 if duration > 95 else 95
        
        # Generator call
        generator = DiffRhythmGenerator()
        return generator.generate.remote(
            lyrics=lyrics,
            genre=genre,
            duration=duration,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.local_entrypoint()
def main():
    """Local test suite."""
    test_request = {
        "request_id": "test_local_01",
        "genre": "indie rock",
        "duration": 95,
        "structure": [
            {
                "type": "verse",
                "start": "00:05.00",
                "lines": ["The neon lights are fading fast", "Memory of a love that didn't last"]
            }
        ]
    }
    print("🎵 Testing optimized system...")
    audio_bytes = process_request.remote(test_request)
    Path("output").mkdir(exist_ok=True)
    with open("output/test_local.wav", "wb") as f:
        f.write(audio_bytes)
    print("✅ Completed local test")
