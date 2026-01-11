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
        
        # Skip empty lines
        if not line:
            errors.append(f"Line {i}: Empty line detected (DiffRhythm doesn't support empty lines)")
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
        
        # Check if there's text after timestamp
        text = line[line.index(']')+1:].strip()
        if not text:
            errors.append(f"Line {i}: Empty text after timestamp")
    
    return len(errors) == 0, errors


def test_lrc_file(json_file: str):
    """Test LRC format in JSON request."""
    
    # Load JSON
    with open(json_file) as f:
        data = json.load(f)
    
    lyrics = data.get('lyrics', '')
    request_id = data.get('request_id', 'unknown')
    
    print(f"Testing: {request_id}")
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
