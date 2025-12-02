# auth.py
from fastapi import Header, HTTPException
from config import API_SECRET_KEY


def verify_api_key(x_api_key: str = Header(...)):
    """Dependency to verify API key from request headers"""
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
