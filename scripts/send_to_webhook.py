import sys
import os
import requests
import json
from pathlib import Path

def send_to_webhook(url, file_paths, metadata=None):
    """
    Fayllari ve metadatani webhook-a gonderir.
    WAV fayllari 'audio' achari ile, MP4 fayllari 'video' achari ile gonderilir.
    """
    payload_files = {}
    opened_files = []
    
    try:
        for path in file_paths:
            p = Path(path)
            if not p.exists():
                print(f"Fayl tapilmadi: {path}")
                continue
            
            f = open(p, 'rb')
            opened_files.append(f)
            
            # Fayl tipine gore achar teyin edirik
            if p.suffix.lower() == '.wav':
                key = 'audio'
            elif p.suffix.lower() == '.mp4':
                key = 'video'
            else:
                key = 'file'
                
            payload_files[key] = (p.name, f)
            print(f"Hazirlanir: {p.name} ({key} olaraq)")

        # Metadata varsa, data hissesine elave edirik
        data = {}
        if metadata:
            data['metadata'] = json.dumps(metadata)
            print("Metadata elave edildi.")

        # POST isteyi
        response = requests.post(url, files=payload_files, data=data)
        
        for f in opened_files:
            f.close()

        if 200 <= response.status_code < 300:
            print(f"Ugurla gonderildi. Status: {response.status_code}")
            return True
        else:
            print(f"Gonderilme ugursuz oldu. Status: {response.status_code}")
            print(f"Cavab: {response.text}")
            return False

    except Exception as e:
        print(f"Xeta: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Istifade: python send_to_webhook.py <url> <fayl1> <fayl2> ...")
        sys.exit(1)

    webhook_url = sys.argv[1]
    file_list = sys.argv[2:]
    
    # Test ucun sade metadata temin edirik
    test_metadata = {
        "source": "github_actions",
        "project": "musicmaker"
    }
    
    success = send_to_webhook(webhook_url, file_list, metadata=test_metadata)
    sys.exit(0 if success else 1)
