import os
import json
import requests
import base64
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Paths
CURRENT_DIR = Path(__file__).resolve().parent
DATA_JSON_FILE_PATH = CURRENT_DIR / 'data.json'

# URLs
CRICFY_BASE = "https://cfyhskssnn99.top"
SPORTZX_API = "https://sportzx.cc/wp-admin/admin-ajax.php?action=vsc_matches"

def decrypt_cricfy(encrypted_base64, secrets):
    try:
        clean_data = encrypted_base64.strip().replace("\n", "").replace("\r", "").replace(" ", "")
        ciphertext = base64.b64decode(clean_data)
        for secret in secrets:
            if not secret or ":" not in secret: continue
            try:
                key_hex, iv_hex = secret.split(":")
                cipher = AES.new(bytes.fromhex(key_hex), AES.MODE_CBC, bytes.fromhex(iv_hex))
                decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
                text = decrypted.decode('utf-8')
                if text.startswith("{") or text.startswith("["): return text
            except: continue
        return None
    except: return None

def main():
    secrets = [os.getenv('CRICFY_SECRET1'), os.getenv('CRICFY_SECRET2')]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    combined_channels = []

    # --- PART 1: Fetch Cricfy Data ---
    print("Fetching Cricfy Events...")
    try:
        c_res = requests.get(f"{CRICFY_BASE}/api/live_events", headers=headers, timeout=10)
        if c_res.status_code == 200:
            for ev in c_res.json():
                slug = ev.get('slug')
                ch_txt = requests.get(f"{CRICFY_BASE}/channels/{slug.lower()}.txt", headers=headers).text
                decrypted = decrypt_cricfy(ch_txt, secrets)
                if decrypted:
                    streams = json.loads(decrypted).get('streamUrls', [])
                    if streams:
                        combined_channels.append({
                            "name": ev.get('title'),
                            "url": streams[0].get('link'),
                            "poster": f"https://live-card-png.cricify.workers.dev/?title={slug}",
                            "source": "Cricfy"
                        })
    except Exception as e: print(f"Cricfy Error: {e}")

    # --- PART 2: Fetch Sportzx Data ---
    print("Fetching Sportzx Events...")
    try:
        s_res = requests.get(SPORTZX_API, headers=headers, timeout=10)
        if s_res.status_code == 200:
            for match in s_res.json():
                # Sirf wo matches lein jo LIVE hain ya jinke links hain
                links = match.get('links', [])
                if links:
                    combined_channels.append({
                        "name": f"{match.get('teamAName')} vs {match.get('teamBName')}",
                        "url": links[0].get('link'),
                        "poster": match.get('eventLogo') or match.get('teamAFlag'),
                        "source": "Sportzx"
                    })
    except Exception as e: print(f"Sportzx Error: {e}")

    # --- Save Combined Data ---
    final_output = {
        "status": "success",
        "total": len(combined_channels),
        "channels": combined_channels
    }
    with open(DATA_JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    print(f"Total {len(combined_channels)} matches saved to data.json")

if __name__ == "__main__":
    main()
                
