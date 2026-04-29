# cli/auth_logic.py
import hashlib
import base64
import secrets

def generate_pkce_data():
    # 1. Create a high-entropy cryptographically strong random string
    code_verifier = secrets.token_urlsafe(64)
    
    # 2. Hash it using SHA-256
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    
    # 3. Base64 encode the hash to create the challenge
    code_challenge = base64.urlsafe_b64encode(hashed).decode('utf-8').replace('=', '')
    
    return code_verifier, code_challenge