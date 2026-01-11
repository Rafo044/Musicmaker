import sys
import os
import requests
from pathlib import Path

def send_to_telegram(token, chat_id, file_paths):
    """
    Fayllari Telegram botu vasitesile gonderir.
    """
    base_url = f"https://api.telegram.org/bot{token}"
    
    for path in file_paths:
        p = Path(path)
        if not p.exists():
            print(f"Fayl tapilmadi: {path}")
            continue
            
        print(f"Telegram-a gonderilir: {p.name}")
        
        # Fayl tipine gore uygun method secilir
        if p.suffix.lower() in ['.mp4', '.mov', '.avi']:
            method = "sendVideo"
            file_key = "video"
        elif p.suffix.lower() in ['.wav', '.mp3', '.m4a']:
            method = "sendAudio"
            file_key = "audio"
        else:
            method = "sendDocument"
            file_key = "document"
            
        url = f"{base_url}/{method}"
        
        with open(p, 'rb') as f:
            payload = {'chat_id': chat_id}
            files = {file_key: f}
            
            response = requests.post(url, data=payload, files=files)
            
            if response.status_code == 200:
                print(f"Ugurla gonderildi: {p.name}")
            else:
                print(f"Gonderilme ugursuz oldu: {p.name}")
                print(f"Status: {response.status_code}")
                print(f"Cavab: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Istifade: python send_to_telegram.py <token> <chat_id> <fayl1> <fayl2> ...")
        sys.exit(1)

    bot_token = sys.argv[1]
    target_chat_id = sys.argv[2]
    files = sys.argv[3:]
    
    send_to_telegram(bot_token, target_chat_id, files)
