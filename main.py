import requests
import json
import re
from pathlib import Path

DATA_JSON_FILE_PATH = Path(__file__).resolve().parent / 'data.json'
SPORTZX_API_URL = "https://sportzx.cc/wp-json/wp/v2/pages?slug=sportzx-live&_fields=content.rendered"

def extract_sportzx_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(SPORTZX_API_URL, headers=headers)
        if response.status_code == 200:
            raw_data = response.json()
            # Content nikalna (Pehla result kyunki slug unique hota hai)
            html_content = raw_data[0]['content']['rendered']
            
            # M3U8 links dhoondhne ke liye Regex use karein
            m3u8_links = re.findall(r'(https?://[^\s\'"]+\.m3u8)', html_content)
            
            # Match titles nikalne ka logic (Ye HTML structure par depend karega)
            # Example: Agar match name <h3> mein hai
            titles = re.findall(r'<h3>(.*?)</h3>', html_content)

            live_channels = []
            for i in range(min(len(titles), len(m3u8_links))):
                live_channels.append({
                    "name": titles[i].strip(),
                    "url": m3u8_links[i],
                    "category": "Live Sports",
                    "poster": "https://sportzx.cc/default-poster.png"
                })

            # data.json mein save karein
            with open(DATA_JSON_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump({"channels": live_channels}, f, indent=4, ensure_ascii=False)
            
            print(f"Sportzx se {len(live_channels)} matches extract ho gaye!")
            
    except Exception as e:
        print(f"Sportzx Fetch Error: {e}")

if __name__ == "__main__":
    extract_sportzx_data()
    
