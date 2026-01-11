#!/usr/bin/env python3
"""Process lyrics-to-song request via Modal.com (DiffRhythm)."""

import sys
import json
from pathlib import Path
import modal


def process_request(json_file: str):
    """
    Process lyrics-to-song request.
    
    Args:
        json_file: Path to JSON request file
    """
    # Load request
    with open(json_file) as f:
        request_data = json.load(f)
    
    print(f"Processing request: {request_data.get('request_id')}")
    print(f"Genre: {request_data.get('genre', 'rock')}")
    
    # Get Modal function (new API)
    process_fn = modal.Function.from_name("musicmaker-diffrhythm", "process_request")
    
    # Call Modal function (returns audio bytes)
    print("🎤 Generating song with vocals...")
    audio_bytes = process_fn.remote(request_data)
    
    # Save to local output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    request_id = request_data.get('request_id', 'unknown')
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{request_id}_{timestamp}.wav"
    output_path = output_dir / filename
    
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    
    print(f"✅ Generation successful!")
    print(f"📁 Saved: {output_path}")
    print(f"📦 Will be uploaded as GitHub Artifact")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_request.py <json_file>")
        sys.exit(1)
    
    try:
        process_request(sys.argv[1])
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        sys.exit(1)
