import os
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    api_key = os.getenv("API_KEY")
    if not api_key:
        # If API_KEY is not set, disable authentication
        return

    if api_key_header is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="API key is missing"
        )
    if api_key_header != api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
