#!/usr/bin/env python3
"""Dry-run test for Modal deployment without GPU usage."""

import sys
import json
from pathlib import Path


def dry_run_test(json_file: str):
    """
    Test all validations without actually deploying.
    
    This simulates the GitHub Actions workflow locally.
    """
    print("DRY RUN TEST - No GPU Usage")
    print("=" * 50)
    print()
    
    # Load JSON
    try:
        with open(json_file) as f:
            data = json.load(f)
        print("Step 1: JSON file loaded")
    except Exception as e:
        print(f"Step 1 FAILED: {e}")
        return False
    
    # Validate schema
    try:
        from jsonschema import validate
        schema_path = Path(__file__).parent.parent / "schemas" / "request.json"
        with open(schema_path) as f:
            schema = json.load(f)
        validate(instance=data, schema=schema)
        print("Step 2: JSON schema valid")
    except Exception as e:
        print(f"Step 2 FAILED: {e}")
        return False
    
    # Validate Lyrics/Structure
    try:
        import re
        lyrics = data.get('lyrics')
        structure = data.get('structure')
        
        if lyrics:
            print("Step 3: Validating LRC format...")
            lines = lyrics.split('\n')
            errors = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue # Allow empty lines in lyrics
                if not line.startswith('['):
                    errors.append(f"Line {i}: No timestamp")
            
            if errors:
                print(f"Step 3 FAILED: LRC errors:")
                for err in errors[:5]:
                    print(f"   - {err}")
                return False
            print("Step 3: LRC format valid")
        elif structure:
            print(f"Step 3: Validating structure ({len(structure)} sections)...")
            for i, section in enumerate(structure):
                if not section.get('type') or not section.get('lines'):
                    print(f"   - Section {i} missing type or lines")
                    return False
            print("Step 3: Structure format valid")
        else:
            print("Step 3 FAILED: Missing both 'lyrics' and 'structure'")
            return False
    except Exception as e:
        print(f"Step 3 FAILED: {e}")
        return False
    
    # Check required fields
    try:
        request_id = data.get('request_id')
        lyrics = data.get('lyrics')
        structure = data.get('structure')
        genre = data.get('genre', 'rock')
        duration = data.get('duration', 95)
        
        if not request_id:
            raise ValueError("Missing request_id")
        if not lyrics and not structure:
            raise ValueError("Missing lyrics/structure")
        if duration < 30 or duration > 600:
            raise ValueError(f"Invalid duration: {duration} (YuE recommended range 30-300s)")
        
        print("Step 4: Required fields present")
        print(f"   - Request ID: {request_id}")
        print(f"   - Genre: {genre}")
        print(f"   - Duration: {duration}s")
        if lyrics:
            print(f"   - Lyrics length: {len(lyrics)} chars")
        if structure:
            total_lines = sum(len(s['lines']) for s in structure)
            print(f"   - Structure: {len(structure)} sections, {total_lines} lines")
    except Exception as e:
        print(f"Step 4 FAILED: {e}")
        return False
    
    # Simulate Modal deployment (without actually deploying)
    print("Step 5: Modal deployment (simulated)")
    print("   - Would deploy to: musicmaker-yue")
    print("   - GPU: A100-40GB (YuE High-Fidelity Stage)")
    print("   - Estimated time: 6-10 minutes (Dual-Stage Generation)")
    print("   - Estimated cost: ~$0.50 - $0.80")
    
    # Simulate video creation
    print("Step 6: Video creation (simulated)")
    print("   - FFmpeg would create MP4")
    print("   - Karaoke subtitles from LRC")
    
    # Simulate uploads
    print("Step 7: Uploads (simulated)")
    print("   - Webhook: Would send WAV + MP4")
    print("   - GitHub Artifacts: Would upload as backup")
    
    print()
    print("=" * 50)
    print("DRY RUN PASSED - Ready for deployment!")
    print("=" * 50)
    print()
    print("💡 To deploy for real:")
    print("   git add requests/")
    print("   git commit -m 'Add: New song'")
    print("   git push")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dry_run.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    try:
        success = dry_run_test(json_file)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Dry run failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
