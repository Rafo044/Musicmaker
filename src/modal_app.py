
import os
import time
import re
from pathlib import Path
import modal

# YuE Model Configuration
# Stage 1: Music Language Modeling (LLaMA-2 7B)
S1_MODEL = "m-a-p/YuE-s1-7B-anneal-en-cot"
# Stage 2: Acoustic Modeling (LLaMA-2 1B)
S2_MODEL = "m-a-p/YuE-s2-1B-general"

# Define Modal App
app = modal.App("musicmaker-yue")

# Shared Volume for Model Cache
volume = modal.Volume.from_name("yue-models", create_if_missing=True)

# Docker Image setup with YuE dependencies
yue_image = (
    modal.Image.from_registry("nvidia/cuda:12.1.0-devel-ubuntu22.04", add_python="3.10")
    .apt_install("git", "ffmpeg", "libsndfile1")
    # Layer 1: Heavy AI Core (Cached separately)
    .pip_install(
        "torch",
        "torchaudio",
        "transformers[audio]>=4.44.0",
        "accelerate>=0.26.0",
    )
    # Layer 2: Build tools & Core YuE dependencies
    .pip_install(
        "wheel",
        "ninja",
        "packaging",
        "xcodec2",
    )
    # Layer 3: Auxiliary dependencies (Audio processing, logging, etc.)
    .pip_install(
        "omegaconf",
        "einops",
        "sentencepiece",
        "tokenizers>=0.19.1",
        "tqdm",
        "tensorboard",
        "matplotlib",
        "PyYAML",
        "scipy",
        "librosa",
        "soundfile",
        "descript-audiotools>=0.7.2",
        "descript-audio-codec",
        "pydantic",
        "jsonschema",
        "requests",
    )
    # Layer 4: Custom compilation
    .run_commands(
        "pip install flash-attn --no-build-isolation"
    )
    # Layer 5: YuE Repositories
    .run_commands(
        "GIT_TERMINAL_PROMPT=0 git clone https://github.com/multimodal-art-projection/YuE.git /root/YuE",
        "GIT_TERMINAL_PROMPT=0 git clone https://huggingface.co/m-a-p/xcodec_mini_infer /root/YuE/inference/xcodec_mini_infer"
    )
)

@app.cls(
    image=yue_image,
    gpu="A100", 
    volumes={"/models": volume},
    timeout=1200,
)
class YuEGenerator:
    s1_path: Path = Path("/models/s1")
    s2_path: Path = Path("/models/s2")

    @modal.enter()
    def download_models(self):
        from huggingface_hub import snapshot_download
        
        if not self.s1_path.exists():
            print(f"📥 Downloading YuE Stage 1 ({S1_MODEL})...")
            snapshot_download(S1_MODEL, local_dir=self.s1_path)
            volume.commit()
            
        if not self.s2_path.exists():
            print(f"📥 Downloading YuE Stage 2 ({S2_MODEL})...")
            snapshot_download(S2_MODEL, local_dir=self.s2_path)
            volume.commit()

    @modal.method()
    def generate(
        self,
        lyrics: str,
        genre: str = "rock",
        duration: int = 95,
        ref_audio_urls: list = None,
    ) -> bytes:
        """
        Produce a full song using YuE (樂) model.
        """
        import subprocess
        import tempfile
        from pathlib import Path
        
        print(f"� YuE Generating: {genre} ({duration}s)")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            
            # 1. Prepare Lyrics and Genre text files (YuE requirement)
            # YuE expects a specific format for lyrics [verse] [chorus]
            lyrics_processed = self._process_lyrics(lyrics)
            lyrics_file = tmp_root / "lyrics.txt"
            lyrics_file.write_text(lyrics_processed)
            
            genre_file = tmp_root / "genre.txt"
            # Enhance genre with benchmark quality tags
            enhanced_genre = f"{genre}. [warm analog tone, mid-range focus, vintage tube compression, thick organic bass, professional mixing]"
            genre_file.write_text(enhanced_genre)
            
            output_dir = tmp_root / "output"
            output_dir.mkdir()

            # Prepare YuE Command
            infer_script = "/root/YuE/inference/infer.py"
            
            # YuE adds 'xcodec_mini_infer' to path automatically in infer.py
            bash_cmd = f"python3 {infer_script} " \
                       f"--stage1_model {self.s1_path} " \
                       f"--stage2_model {self.s2_path} " \
                       f"--genre_txt {genre_file} " \
                       f"--lyrics_txt {lyrics_file} " \
                       f"--run_n_segments 2 " \
                       f"--output_dir {output_dir} " \
                       f"--cuda_idx 0 " \
                       f"--max_new_tokens 3000"

            print(f"🚀 Executing High-Fidelity YuE Engine: {bash_cmd}")
            
            process = subprocess.run(
                ["bash", "-c", bash_cmd],
                capture_output=True,
                text=True,
                cwd="/root/YuE/inference" # Run from inference dir where infer.py lives
            )
            
            if process.returncode != 0:
                print(f"❌ YuE Failed: {process.stderr}")
                raise RuntimeError(f"YuE Inference Error: {process.stderr}")

            # Collect output
            output_files = list(output_dir.glob("*.mp3")) or list(output_dir.glob("*.wav"))
            if not output_files:
                raise RuntimeError("YuE did not generate any audio files.")
                
            with open(output_files[0], "rb") as f:
                return f.read()

    def _process_lyrics(self, raw_lyrics: str) -> str:
        """
        Convert timestamped LRC or plain text to YuE format.
        YuE format: 
        [verse]
        Lyric lines...
        [chorus]
        Lyric lines...
        """
        # Remove timestamps if present
        clean = re.sub(r'\[\d{2}:\d{2}\.\d{2}\]', '', raw_lyrics)
        
        # Ensure section tags are lowercase and bracketed
        clean = re.sub(r'(Verse|Chorus|Intro|Outro|Bridge)', r'[\1]', clean, flags=re.IGNORECASE)
        clean = clean.lower()
        
        return clean.strip()

@app.function(image=yue_image, timeout=300)
def process_request(data: dict):
    """
    Gateway function for processing requests.
    """
    lyrics = data.get("lyrics")
    # If using structure format, convert it
    if "structure" in data and not lyrics:
        lyrics = ""
        for section in data["structure"]:
            lyrics += f"\n[{section['type']}]\n"
            lyrics += "\n".join(section["lines"])
    
    genre = data.get("genre", "rock")
    duration = data.get("duration", 95)
    ref_audio_urls = data.get("ref_audio_urls", [])

    gen = YuEGenerator()
    audio_bytes = gen.generate.remote(
        lyrics=lyrics,
        genre=genre,
        duration=duration,
        ref_audio_urls=ref_audio_urls
    )
    
    return audio_bytes
