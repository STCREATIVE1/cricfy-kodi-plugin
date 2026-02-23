import os
import json
import requests
import base64
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Paths setup
CURRENT_DIR = Path(__file__).resolve().parent
DATA_JSON_FILE_PATH = CURRENT_DIR / 'data.json'

# Updated Base URL
BASE_URL = "https://cfyhskssnn99.top"

def hex_to_bytes(hex_str):
    """Hex string to byte array converter."""
    return bytes.fromhex(hex_str)

def decrypt_data(encrypted_base64, secrets):
    """AES/CBC/PKCS5Padding decryption."""
    try:
        clean_data = encrypted_base64.strip().replace("\n", "").replace("\r", "").replace(" ", "")
        ciphertext = base64.b64decode(clean_data)
        
        for secret in secrets:
            if not secret or ":" not in secret:
                continue
            
            try:
                key_hex, iv_hex = secret.split(":")
                key = hex_to_bytes(key_hex)
                iv = hex_to_bytes(iv_hex)
                
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
                text = decrypted.decode('utf-8')
                
                if text.startswith("{") or text.startswith("[") or "http" in text.lower():
                    return text
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None

def main():
    # Fetch secrets from GitHub Actions environment
    s1 = os.getenv('CRICFY_SECRET1')
    s2 = os.getenv('CRICFY_SECRET2')
    secrets_list = [s1, s2]

    # Enhanced headers to mimic a mobile device
    headers = {
        "User-Agent": "Cricfy/1.0 (Android 11; Realme P1 5G)",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "Accept": "application/json"
    }

    print(f"Connecting to: {BASE_URL}")
    
    try:
        # 1. Fetch Live Events (Checking common API paths from dex analysis)
        api_path = "/api/live_events" 
        response = requests.get(f"{BASE_URL}{api_path}", headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Primary API failed. Status: {response.status_code}. Trying fallback...")
            # Fallback path if the primary one is blocked
            response = requests.get(f"{BASE_URL}/api/v1/live_events", headers=headers, timeout=15)

        if response.status_code != 200:
            print("Could not fetch events from any known API path.")
            return

        events = response.json()
        live_channels = []

        # 2. Process each event
        for event in events:
            slug = event.get('slug')
            if not slug:
                continue

            # Fetch encrypted channel data
            channel_url = f"{BASE_URL}/channels/{slug.lower()}.txt"
            ch_res = requests.get(channel_url, headers=headers, timeout=10)
            
            if ch_res.status_code == 200:
                decrypted_text = decrypt_data(ch_res.text, secrets_list)
                
                if decrypted_text:
                    channel_data = json.loads(decrypted_text)
                    streams = channel_data.get('streamUrls', [])
                    
                    if streams:
                        stream_info = streams[0]
                        live_channels.append({
                            "name": event.get('title', 'Live Match'),
                            "slug": slug,
                            "url": stream_info.get('link'),
                            "category": event.get('cat', 'Sports'),
                            "poster": f"https://live-card-png.cricify.workers.dev/?title={slug}&isLive=true",
                            "is_drm": stream_info.get('type') == "7"
                        })

        # 3. Save to data.json for the streaming project
        final_data = {
            "status": "success",
            "last_updated": "2026-02-23",
            "channels": live_channels
        }

        with open(DATA_JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully generated data.json with {len(live_channels)} channels.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
            
