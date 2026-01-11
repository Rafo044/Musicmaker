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
        ref_audio_urls: list = None,
    ) -> bytes:
        """
        Generate full song from lyrics with optional reference audios.
        """
        import subprocess
        import tempfile
        import requests
        from pathlib import Path
        
        start_time = time.time()
        ref_audio_urls = ref_audio_urls or []
        
        print(f"🎤 Generating {genre} song ({duration}s) with {len(ref_audio_urls)} references")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            lyrics_file = tmpdir / "lyrics.lrc"
            
            # Download reference audios
            local_ref_paths = []
            for i, url in enumerate(ref_audio_urls):
                try:
                    ref_path = tmpdir / f"ref_{i}.wav"
                    print(f"Downloading reference style: {url}")
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        ref_path.write_bytes(resp.content)
                        local_ref_paths.append(ref_path)
                except Exception as e:
                    print(f"Warning: Failed to download style ref {url}: {e}")

            # Clean lyrics logic
            clean_lyrics = []
            for line in lyrics.split('\n'):
                line = re.sub(r'(\[\d{2}:\d{2}\.\d{2}\])\s*(Verse|Chorus|Intro|Outro|Bridge|Solo|Hook|Header).*', r'\1', line, flags=re.IGNORECASE)
                if re.search(r'\]\s*\S+', line):
                    line = re.sub(r'\]\s*', r'] ', line)
                    clean_lyrics.append(line.strip())
            
            lyrics_file.write_text('\n'.join(clean_lyrics))
            
            # Prepare DiffRhythm Command
            cmd = [
                "python3", "/root/DiffRhythm/infer/infer.py",
                "--lrc-path", str(lyrics_file),
                "--audio-length", str(duration),
                "--output-dir", str(tmpdir),
                "--chunked"
            ]

            # Logic: If Audio Reference exists, WE MUST NOT use --ref-prompt (AssertionError Fix)
            if local_ref_paths:
                print(f"Blending {len(local_ref_paths)} reference styles into one...")
                blended_ref = tmpdir / "blended_style.wav"
                
                if len(local_ref_paths) > 1:
                    # Stitch audios together using FFmpeg
                    # Each input -i file, then filter_complex to concat audio (v=0, a=1)
                    inputs = []
                    for p in local_ref_paths:
                        inputs.extend(["-i", str(p)])
                    
                    filter_str = "".join([f"[{i}:a]" for i in range(len(local_ref_paths))])
                    filter_str += f"concat=n={len(local_ref_paths)}:v=0:a=1[aout]"
                    
                    ffmpeg_cmd = ["ffmpeg"] + inputs + ["-filter_complex", filter_str, "-map", "[aout]", str(blended_ref)]
                    subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                else:
                    # Just one file, copy it
                    import shutil
                    shutil.copy(local_ref_paths[0], blended_ref)
                
                cmd.extend(["--ref-audio-path", str(blended_ref)])
            else:
                # Use text prompt ONLY if no audio reference is provided
                enhanced_genre = f"{genre}, studio recording, clear dry vocals, steady rhythm, high fidelity"
                cmd.extend(["--ref-prompt", enhanced_genre])
            
            print(f"Executing DiffRhythm High-End Production...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/root/DiffRhythm",
                env={**os.environ, "PYTHONPATH": "/root/DiffRhythm"}
            )
            
            if result.returncode != 0:
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"DiffRhythm failed: {result.stderr}")
            
            generated_files = list(tmpdir.glob("*.wav"))
            if not generated_files:
                raise RuntimeError("No output file generated")
            
            with open(generated_files[0], "rb") as f:
                audio_bytes = f.read()
        
        return audio_bytes


def check_url(url: str) -> bool:
    """Shield: Verify if the URL is accessible before starting GPU generation."""
    import requests
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


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
    """Process lyrics-to-song request with URL Shield."""
    try:
        # Extract parameters
        lyrics = get_lyrics_from_data(request_data)
        genre = request_data.get("genre", "rock")
        duration = request_data.get("duration", 95)
        ref_urls = request_data.get("ref_audio_urls", [])
        
        # URL Shield: Prevent execution if any reference URL is broken
        for url in ref_urls:
            print(f"Checking URL Shield: {url}")
            if not check_url(url):
                raise ValueError(f"CRITICAL: Reference URL is broken or inaccessible: {url}. Generation aborted.")
        
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
            ref_audio_urls=ref_urls,
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
