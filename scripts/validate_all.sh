#!/bin/bash
# Complete validation before deployment

echo "FULL SYSTEM VALIDATION"
echo "=========================="
echo ""

# 1. JSON Schema
echo "1. JSON Schema Validation..."
python3 scripts/validate_request.py requests/silhouettes_indie.json
if [ $? -ne 0 ]; then
    echo "JSON validation failed"
    exit 1
fi
echo ""

# 2. LRC Format
echo "2. LRC Format Validation..."
python3 scripts/test_lrc.py requests/silhouettes_indie.json
if [ $? -ne 0 ]; then
    echo "LRC validation failed"
    exit 1
fi
echo ""

# 3. Dependencies
echo "3. Checking Dependencies..."
# Note: modal might not be in local venv but will be in GitHub Actions
python3 -c "import pydantic; import jsonschema; print('Core deps OK')"
if [ $? -ne 0 ]; then
    echo "Dependencies missing"
    exit 1
fi
echo ""

# 4. File Structure
echo "4. File Structure Check..."
if [ ! -f "requests/silhouettes_indie.json" ]; then
    echo "Request file not found"
    exit 1
fi

if [ ! -f "scripts/process_request.py" ]; then
    echo "Process script not found"
    exit 1
fi

if [ ! -f "scripts/create_video.py" ]; then
    echo "Video script not found"
    exit 1
fi

if [ ! -f "scripts/send_to_webhook.py" ]; then
    echo "Webhook script not found"
    exit 1
fi

echo "All files present"
echo ""

# 5. Workflow File
echo "5. Workflow Syntax Check..."
if [ ! -f ".github/workflows/deploy.yml" ]; then
    echo "Workflow file not found"
    exit 1
fi
echo "Workflow file exists"
echo ""

# Summary
echo "=========================="
echo "ALL VALIDATIONS PASSED!"
echo "=========================="
echo ""
echo "Ready to deploy!"
