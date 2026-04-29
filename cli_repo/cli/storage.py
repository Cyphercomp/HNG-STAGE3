# cli/storage.py
import os
import json

CREDENTIALS_PATH = os.path.expanduser("~/.insighta/credentials.json")

def save_credentials(data):
    os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
    with open(CREDENTIALS_PATH, 'w') as f:
        json.dump({
            "access_token": data['access_token'],
            "refresh_token": data['refresh_token']
        }, f)

def get_tokens():
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    with open(CREDENTIALS_PATH, 'r') as f:
        return json.load(f)