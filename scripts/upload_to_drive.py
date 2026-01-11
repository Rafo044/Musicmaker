#!/usr/bin/env python3
"""Upload generated music/video to Google Drive."""

import sys
import json
import os
from pathlib import Path
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path: str, folder_id: str):
    """Upload using OAuth2 Refresh Token."""
    
    # GitHub Secrets-dən gələn məlumatlar
    client_id = os.getenv('GDRIVE_CLIENT_ID')
    client_secret = os.getenv('GDRIVE_CLIENT_SECRET')
    refresh_token = os.getenv('GDRIVE_REFRESH_TOKEN')
    
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    
    # Refresh token if expired
    if creds.expired:
        creds.refresh(google.auth.transport.requests.Request())

    service = build('drive', 'v3', credentials=creds)
    
    file_name = Path(file_path).name
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(file_path, resumable=True)
    
    print(f"📤 Uploading {file_name} as your user account...")
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    print(f"✅ Uğurla sənin Drive-na yükləndi!")
    return file.get('id'), file.get('webViewLink')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_to_drive.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Get credentials from environment
    client_id = os.getenv('GDRIVE_CLIENT_ID')
    client_secret = os.getenv('GDRIVE_CLIENT_SECRET')
    refresh_token = os.getenv('GDRIVE_REFRESH_TOKEN')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Error: Google Drive OAuth2 credentials (ID, Secret, or Refresh Token) not set")
        sys.exit(1)
    
    if not folder_id:
        print("❌ Error: GOOGLE_DRIVE_FOLDER_ID not set")
        sys.exit(1)
    
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        file_id, link = upload_to_drive(file_path, folder_id)
        
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
