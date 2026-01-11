#!/usr/bin/env python3
"""Test LRC format for DiffRhythm compatibility."""

import sys
import json
import re
from pathlib import Path


def validate_lrc_format(lyrics: str) -> tuple[bool, list[str]]:
    """
    Validate LRC format for DiffRhythm.
    
    Returns:
        (is_valid, errors)
    """
    errors = []
    lines = lyrics.split('\n')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip truly empty lines (DiffRhythm will ignore them)
        if not line:
            continue
        
        # Check LRC format
        if not line.startswith('['):
            errors.append(f"Line {i}: Missing timestamp - '{line[:50]}...'")
            continue
        
        # Check timestamp format [MM:SS.mm]
        timestamp_match = re.match(r'\[(\d{2}):(\d{2}\.\d{2})\]', line)
        if not timestamp_match:
            errors.append(f"Line {i}: Invalid timestamp format - '{line[:30]}...'")
            continue
        
        # Note: We allow empty text after timestamps for instrumental/silence parts.
    
    return len(errors) == 0, errors


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


def test_lrc_file(json_file: str):
    """Test LRC format in JSON request."""
    
    # Load JSON
    with open(json_file) as f:
        data = json.load(f)
    
    lyrics = get_lyrics_from_data(data)
    request_id = data.get('request_id', 'unknown')
    
    print(f"Testing: {request_id}")
    if not lyrics:
        print("Error: No lyrics or structure found")
        return False
        
    print(f"Lyrics length: {len(lyrics)} characters")
    print(f"Lines: {len(lyrics.split(chr(10)))}")
    
    # Validate
    is_valid, errors = validate_lrc_format(lyrics)
    
    if is_valid:
        print(f"\nLRC format is VALID!")
        print(f"Ready for DiffRhythm")
        return True
    else:
        print(f"\nLRC format has ERRORS:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_lrc.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"File not found: {json_file}")
        sys.exit(1)
    
    try:
        is_valid = test_lrc_file(json_file)
        sys.exit(0 if is_valid else 1)
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
