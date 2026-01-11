import os
import sys
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_gdrive_service():
    """Build and return a Google Drive service object."""
    client_id = os.environ.get("GDRIVE_CLIENT_ID")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET")
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing Google Drive credentials (ClientID, Secret, or RefreshToken)")
        return None

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    if not creds.valid:
        creds.refresh(Request())

    return build("drive", "v3", credentials=creds)

def upload_files(folder_id, local_dir="output"):
    """Upload all files from local_dir to Google Drive folder."""
    service = get_gdrive_service()
    if not service:
        return

    output_path = Path(local_dir)
    if not output_path.exists():
        print(f"Warning: Directory {local_dir} exist.")
        return

    files_to_upload = list(output_path.glob("*.wav")) + list(output_path.glob("*.mp4"))
    
    if not files_to_upload:
        print("No files found to upload.")
        return

    for file_path in files_to_upload:
        print(f"Uploading {file_path.name}...")
        
        file_metadata = {
            "name": file_path.name,
            "parents": [folder_id] if folder_id else []
        }
        
        media = MediaFileUpload(str(file_path), resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        
        print(f"Uploaded! Drive File ID: {file.get('id')}")

if __name__ == "__main__":
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    local_dir = "output"
    
    if len(sys.argv) > 1:
        local_dir = sys.argv[1]
        
    upload_files(folder_id, local_dir)
