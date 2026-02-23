import os
import json
import requests
import base64
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

CURRENT_DIR = Path(__file__).resolve().parent
DATA_JSON_FILE_PATH = CURRENT_DIR / 'data.json'
BASE_URL = "Https://cfyhskssnn99.top"

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def decrypt_data(encrypted_base64, secrets):
    """Aapke CryptoUtils ka Python version jo AES/CBC/PKCS5Padding use karta hai."""
    try:
        # Clean base64 string
        clean_data = encrypted_base64.strip().replace("\n", "").replace("\r", "")
        ciphertext = base64.b64decode(clean_data)
        
        for secret in secrets:
            if not secret or ":" not in secret: continue
            
            try:
                # Split Key and IV
                key_hex, iv_hex = secret.split(":")
                key = hex_to_bytes(key_hex)
                iv = hex_to_bytes(iv_hex)
                
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
                text = decrypted.decode('utf-8')
                
                # Validation
                if text.startswith("{") or text.startswith("[") or "http" in text.lower():
                    return text
            except:
                continue
        return None
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def main():
    # Secrets fetch karna
    s1 = os.getenv('CRICFY_SECRET1')
    s2 = os.getenv('CRICFY_SECRET2')
    secrets_list = [s1, s2]

    print("Fetching Live Events...")
    try:
        # 1. Live Events fetch karein
        # Cricfy typically provides events at this or similar endpoint
        res = requests.get(f"{BASE_URL}/api/live_events", timeout=15)
        if res.status_code != 200:
            print("Failed to fetch events list.")
            return

        events = res.json()
        live_channels = []

        for event in events:
            slug = event.get('slug')
            if not slug: continue

            # 2. Encrypted slug.txt fetch karein
            ch_res = requests.get(f"{BASE_URL}/channels/{slug.lower()}.txt", timeout=10)
            if ch_res.status_code == 200:
                decrypted_text = decrypt_data(ch_res.text, secrets_list)
                
                if decrypted_text:
                    channel_data = json.loads(decrypted_text)
                    # Extracting first available stream link
                    streams = channel_data.get('streamUrls', [])
                    if streams:
                        live_channels.append({
                            "name": event.get('title', 'Live Match'),
                            "category": event.get('cat', 'Sports'),
                            "url": streams[0].get('link'),
                            "poster": f"https://live-card-png.cricify.workers.dev/?title={slug}&isLive=true",
                            "type": "live"
                        })

        # 3. Final data.json save karein
        with open(DATA_JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({"channels": live_channels}, f, indent=4, ensure_ascii=False)
            
        print(f"Done! {len(live_channels)} channels decrypted and saved.")

    except Exception as e:
        print(f"Main Loop Error: {e}")

if __name__ == "__main__":
    main()
        
