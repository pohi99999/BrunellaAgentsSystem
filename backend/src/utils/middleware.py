
import os
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, public_paths: set[str] | None = None):
        super().__init__(app)
        self.public_paths = public_paths or set()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.public_paths:
            return await call_next(request)

        api_key = os.getenv("API_KEY")
        if not api_key:
            # If no API key is configured on the server, allow access
            return await call_next(request)

        api_key_header = request.headers.get("X-API-Key")
        if not api_key_header:
            logger.warning(
                "API request rejected: Missing API Key from %s to %s",
                request.client.host if request.client else "unknown",
                request.url.path,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing API Key"},
            )

        if api_key_header != api_key:
            logger.warning(
                "API request rejected: Invalid API Key from %s to %s",
                request.client.host if request.client else "unknown",
                request.url.path,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API Key"},
            )

        return await call_next(request)
