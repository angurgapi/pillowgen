# config.py
import os
from pathlib import Path

# Path to store the API key persistently
KEY_FILE = Path(__file__).parent / ".api_key"

def get_or_create_api_key():
    """Get existing API key or create a new one and persist it."""
    # First check environment variable
    env_key = os.environ.get("API_SECRET_KEY")
    if env_key:
        return env_key
    
    # Check if key file exists
    if KEY_FILE.exists():
        with open(KEY_FILE, 'r') as f:
            return f.read().strip()
    
    # Generate new key and save it
    import secrets
    new_key = secrets.token_urlsafe(32)
    with open(KEY_FILE, 'w') as f:
        f.write(new_key)
    
    print(f"\n{'='*60}")
    print(f"🔑 Generated new API Secret Key: {new_key}")
    print(f"Saved to: {KEY_FILE}")
    print(f"This key will persist across restarts.")
    print(f"To use a custom key, set the API_SECRET_KEY environment variable")
    print(f"{'='*60}\n")
    
    return new_key

API_SECRET_KEY = get_or_create_api_key()
