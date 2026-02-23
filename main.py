from pathlib import Path
import os
import json

CURRENT_DIR = Path(__file__).resolve().parent
CRICFY_PLUGIN_DIR = CURRENT_DIR / 'plugin.video.cricfy'
CRICFY_PLUGIN_RESOURCES_DIR = CRICFY_PLUGIN_DIR / 'resources'

CRICFY_SECRET1_FILE_PATH = CRICFY_PLUGIN_RESOURCES_DIR / 'secret1.txt'
CRICFY_SECRET2_FILE_PATH = CRICFY_PLUGIN_RESOURCES_DIR / 'secret2.txt'
CRICFY_PROPERTIES_FILE_PATH = CRICFY_PLUGIN_RESOURCES_DIR / 'cricfy_properties.json'

# Nayi file ka path root directory mein
DATA_JSON_FILE_PATH = CURRENT_DIR / 'data.json'

def main():
  CRICFY_FIREBASE_API_KEY = os.getenv('CRICFY_FIREBASE_API_KEY')
  CRICFY_FIREBASE_APP_ID = os.getenv('CRICFY_FIREBASE_APP_ID')
  CRICFY_PACKAGE_NAME = os.getenv('CRICFY_PACKAGE_NAME')
  CRICFY_SECRET1 = os.getenv('CRICFY_SECRET1')
  CRICFY_SECRET2 = os.getenv('CRICFY_SECRET2')

  if (
    not CRICFY_FIREBASE_API_KEY
    or not CRICFY_FIREBASE_APP_ID
    or not CRICFY_PACKAGE_NAME
    or (not CRICFY_SECRET1 and not CRICFY_SECRET2)
  ):
    raise Exception("Required environment variables not set.")

  # Secrets save karna
  if CRICFY_SECRET1:
    with open(CRICFY_SECRET1_FILE_PATH, 'w') as f:
      f.write(CRICFY_SECRET1)

  if CRICFY_SECRET2:
    with open(CRICFY_SECRET2_FILE_PATH, 'w') as f:
      f.write(CRICFY_SECRET2)

  # Properties file create karna
  cricfy_properties = {
    "cricfy_firebase_api_key": CRICFY_FIREBASE_API_KEY,
    "cricfy_firebase_app_id": CRICFY_FIREBASE_APP_ID,
    "cricfy_package_name": CRICFY_PACKAGE_NAME
  }
  
  with open(CRICFY_PROPERTIES_FILE_PATH, 'w') as f:
    json.dump(cricfy_properties, f, separators=(',', ':'))

  # --- NAYA LOGIC: data.json create karna ---
  # Isme hum wahi data daal rahe hain jo ELITE STREAM PRO ke liye zaroori ho sakta hai
  combined_data = {
    "status": "success",
    "config": cricfy_properties,
    "version": "1.0.0"
  }

  with open(DATA_JSON_FILE_PATH, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, indent=4)
  # ------------------------------------------

  print("All Operations completed successfully. data.json has been created.")


if __name__ == "__main__":
  main()
