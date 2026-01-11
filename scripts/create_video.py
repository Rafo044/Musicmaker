#!/usr/bin/env python3
"""Create video from audio and background image with lyrics."""

import sys
import json
import subprocess
import re
from pathlib import Path


def lrc_to_srt(lrc_text: str, output_srt: Path):
    """
    Convert LRC format to SRT format.
    
    Args:
        lrc_text: Lyrics in LRC format
        output_srt: Output SRT file path
    """
    lines = lrc_text.strip().split('\n')
    srt_lines = []
    index = 1
    
    for i, line in enumerate(lines):
        if not line.strip() or not line.startswith('['):
            continue
        
        # Parse LRC timestamp [MM:SS.mm]
        try:
            timestamp_end = line.index(']')
            timestamp = line[1:timestamp_end]
            text = line[timestamp_end + 1:].strip()
            
            if not text:
                continue
            
            # Convert to SRT format
            minutes, seconds = timestamp.split(':')
            seconds, centiseconds = seconds.split('.')
            
            # Start time
            start_time = f"00:{minutes.zfill(2)}:{seconds.zfill(2)},{centiseconds.ljust(3, '0')}"
            
            # End time (next line or +5 seconds)
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.startswith('['):
                    next_timestamp_end = next_line.index(']')
                    next_timestamp = next_line[1:next_timestamp_end]
                    next_minutes, next_seconds = next_timestamp.split(':')
                    next_seconds, next_centiseconds = next_seconds.split('.')
                    end_time = f"00:{next_minutes.zfill(2)}:{next_seconds.zfill(2)},{next_centiseconds.ljust(3, '0')}"
                else:
                    # Default +5 seconds
                    end_seconds = int(seconds) + 5
                    end_time = f"00:{minutes.zfill(2)}:{str(end_seconds).zfill(2)},{centiseconds.ljust(3, '0')}"
            else:
                # Last line, +5 seconds
                end_seconds = int(seconds) + 5
                end_time = f"00:{minutes.zfill(2)}:{str(end_seconds).zfill(2)},{centiseconds.ljust(3, '0')}"
            
            # SRT format
            srt_lines.append(f"{index}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")
            
            index += 1
            
        except (ValueError, IndexError) as e:
            print(f"⚠️  Skipping invalid line: {line}")
            continue
    
    # Write SRT file
    with open(output_srt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_lines))
    
    print(f"✅ Created SRT file: {output_srt}")


def create_video(audio_path: str, image_path: str, srt_path: str, output_path: str):
    """
    Create video using FFmpeg.
    
    Args:
        audio_path: Path to audio file (WAV)
        image_path: Path to background image
        srt_path: Path to SRT subtitles
        output_path: Output video path (MP4)
    """
    # High-End Cinematic Subtitle Style (Minimalist & Professional):
    # BorderStyle=1, Thin Outline (0.5), Soft Shadow (0.5), Semi-transparent Outline.
    force_style = (
        "FontName=Arial,"
        "FontSize=18,"
        "PrimaryColour=&H00FFFFFF&,"   # Solid White
        "OutlineColour=&H66222222&,"   # Semi-transparent dark grey outline
        "BorderStyle=1,"
        "Outline=0.5,"
        "Shadow=0.5,"
        "ShadowColour=&H88000000&,"
        "Alignment=2,"
        "MarginV=60"                    # Balanced lower third
    )
    
    cmd = [
        'ffmpeg', '-loop', '1', '-i', image_path,
        '-i', audio_path,
        '-vf', f"subtitles={srt_path}:force_style='{force_style}'",
        '-c:v', 'libx264', '-tune', 'stillimage',
        '-c:a', 'aac', '-b:a', '256k', # Higher audio bitrate for MP4
        '-pix_fmt', 'yuv420p',
        '-sn',  # Kill embedded subs to prevent doubling
        '-shortest', '-y', output_path
    ]
    
    print(f"🎬 Creating video with FFmpeg...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ FFmpeg error: {result.stderr}")
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")
    
    print(f"✅ Video created: {output_path}")


def get_lyrics_from_data(data: dict) -> str:
    """Extract or generate LRC lyrics from request data."""
    lyrics_text = data.get('lyrics', '')
    structure = data.get('structure', [])
    
    if structure:
        import re
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
                    line_total = base_total + (i * 4.0)
                    m = int(line_total // 60)
                    s = line_total % 60
                    lrc_lines.append(f"[{m:02d}:{s:05.2f}] {line}")
        return "\n".join(lrc_lines)
    return lyrics_text


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_video.py <request_json> <audio_file>")
        sys.exit(1)
    
    request_json = sys.argv[1]
    audio_file = sys.argv[2]
    
    # Load request
    with open(request_json) as f:
        request_data = json.load(f)
    
    lyrics = get_lyrics_from_data(request_data)
    request_id = request_data.get('request_id', 'unknown')
    
    if not lyrics:
        print("❌ No lyrics or structure found in request")
        sys.exit(1)
    
    # Paths
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    srt_path = output_dir / f"{request_id}.srt"
    video_path = output_dir / f"{request_id}.mp4"
    
    # Default background image
    image_path = Path("images/background.jpg")
    if not image_path.exists():
        print(f"Background image not found: {image_path}")
        print("Creating default black background...")
        # Create black image with FFmpeg
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'color=c=black:s=1920x1080:d=1',
            '-frames:v', '1', '-y', str(image_path)
        ], check=True)
    
    try:
        # Convert LRC to SRT
        lrc_to_srt(lyrics, srt_path)
        
        # Create video
        create_video(str(audio_file), str(image_path), str(srt_path), str(video_path))
        
        print(f"\nVideo generation complete!")
        print(f"Video: {video_path}")
        print(f"Size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"Video creation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
