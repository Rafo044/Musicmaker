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
    # Use .strip() to prevent 'invalid_client' errors due to hidden spaces in secrets
    client_id = os.environ.get("GDRIVE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN", "").strip()

    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing Google Drive credentials (GDRIVE_CLIENT_ID, SECRET, or REFRESH_TOKEN)")
        return None

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    if not creds.valid:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error: Refreshing token failed. This is often due to invalid Client ID/Secret or Expired Refresh Token.")
            print(f"Technical Error: {e}")
            raise

    return build("drive", "v3", credentials=creds)

def check_file_exists(service, name, folder_id):
    """Check if a file with the same name exists in the target folder."""
    # Search for the exact name in the specific parent folder
    query = f"name = '{name}' and '{folder_id}' in parents and trashed = false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    return response.get('files', [])

def upload_files(folder_id, local_dir="output"):
    """Upload all files from local_dir to Google Drive if they don't exist."""
    service = get_gdrive_service()
    if not service:
        return

    output_path = Path(local_dir)
    if not output_path.exists():
        print(f"Warning: Directory {local_dir} does not exist.")
        return

    files_to_upload = list(output_path.glob("**.wav")) + list(output_path.glob("**.mp4"))
    
    if not files_to_upload:
        print("No files found to upload.")
        return

    for file_path in files_to_upload:
        # Check if already exists to ensure sync logic
        existing_files = check_file_exists(service, file_path.name, folder_id)
        if existing_files:
            print(f"Skipping {file_path.name} (already exists on Drive)")
            continue

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
