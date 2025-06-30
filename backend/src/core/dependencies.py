from fastapi import Header, HTTPException

from src.core.config import settings


def validate_api_token_header(api_token: str = Header()):
    if api_token != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
