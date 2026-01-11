import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Bu scripti öz kompüterində işlət (Cloud-da yox)
# Səndən Client ID və Secret soruşacaq

def get_refresh_token():
    client_id = input("Client ID daxil et: ")
    client_secret = input("Client Secret daxil et: ")
    
    config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    
    flow = InstalledAppFlow.from_client_config(
        config,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    
    creds = flow.run_local_server(port=0)
    
    print("\n" + "="*50)
    print("SƏNİN REFRESH TOKENİN:")
    print(creds.refresh_token)
    print("="*50)
    print("\nBu tokeni, Client ID-ni və Secret-i GitHub Secrets-ə əlavə et.")

if __name__ == "__main__":
    get_refresh_token()
