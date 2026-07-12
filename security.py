from fastapi import Header, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
import config

# Rate limiter — tracks requests per client IP
limiter = Limiter(key_func=get_remote_address)


def verify_api_key(x_api_key: str = Header(...)):
    """Checks the incoming request's API key against the one in .env"""
    if x_api_key != config.APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def validate_query(question: str):
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    word_count = len(question.split())
    if word_count > 100:
        raise HTTPException(status_code=400, detail="Question is too long — keep it under 100 words")