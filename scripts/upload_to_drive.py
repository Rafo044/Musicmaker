#!/usr/bin/env python3
"""Upload generated music/video to Google Drive."""

import sys
import json
import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_drive(file_path: str, folder_id: str, credentials_json: str):
    """
    Upload file to Google Drive.
    
    Args:
        file_path: Path to file to upload
        folder_id: Google Drive folder ID
        credentials_json: Service account credentials (JSON string)
    
    Returns:
        File ID and shareable link
    """
    # Parse credentials
    credentials_dict = json.loads(credentials_json)
    
    # Create credentials
    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    
    # Build Drive service
    service = build('drive', 'v3', credentials=credentials)
    
    # File metadata
    file_name = Path(file_path).name
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    # Upload file
    media = MediaFileUpload(file_path, resumable=True)
    
    print(f"📤 Uploading {file_name} to Google Drive...")
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, webContentLink'
    ).execute()
    
    file_id = file.get('id')
    web_view_link = file.get('webViewLink')
    
    print(f"✅ Upload successful!")
    print(f"📁 File ID: {file_id}")
    print(f"🔗 Link: {web_view_link}")
    
    return file_id, web_view_link


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_to_drive.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Get credentials from environment
    credentials_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not credentials_json:
        print("❌ Error: GOOGLE_DRIVE_CREDENTIALS not set")
        sys.exit(1)
    
    if not folder_id:
        print("❌ Error: GOOGLE_DRIVE_FOLDER_ID not set")
        sys.exit(1)
    
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        file_id, link = upload_to_drive(file_path, folder_id, credentials_json)
        
        # Save link to file for GitHub Actions
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "drive_link.txt", "w") as f:
            f.write(link)
        
        print(f"\n🎉 File uploaded successfully!")
        print(f"🔗 Access link saved to: output/drive_link.txt")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
