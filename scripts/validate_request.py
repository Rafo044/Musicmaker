#!/usr/bin/env python3
"""Validate music generation request JSON against schema."""

import sys
import json
from pathlib import Path
from jsonschema import validate, ValidationError


def validate_request(json_file: str) -> bool:
    """
    Validate request JSON against schema.
    
    Args:
        json_file: Path to JSON file
        
    Returns:
        True if valid, raises exception otherwise
    """
    # Load schema
    schema_path = Path(__file__).parent.parent / "schemas" / "request.json"
    with open(schema_path) as f:
        schema = json.load(f)
    
    # Load request
    with open(json_file) as f:
        request = json.load(f)
    
    # Validate
    try:
        validate(instance=request, schema=schema)
        print(f"✅ Valid: {json_file}")
        return True
    except ValidationError as e:
        print(f"❌ Invalid: {json_file}")
        print(f"Error: {e.message}")
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_request.py <json_file>")
        sys.exit(1)
    
    try:
        validate_request(sys.argv[1])
    except Exception as e:
        print(f"Validation failed: {e}")
        sys.exit(1)
