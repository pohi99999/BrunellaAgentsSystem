
import os
import pathlib
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.specialists.coder_agent import coder_chain
from src.utils.middleware import APIKeyMiddleware
from src.utils.prompt_validator import validate_prompt
from src.utils.logging_config import setup_logging

# Setup logging at module level (before app creation)
setup_logging()
logger = logging.getLogger(__name__)

# Define rate limiter
limiter = Limiter(key_func=get_remote_address)

# Define the FastAPI app
app = FastAPI(title="Brunella Agent Server")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add the API Key middleware, excluding the /health endpoint
app.add_middleware(APIKeyMiddleware, public_paths={"/health"})

# Environment-aware CORS configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


ALLOWED_LANGUAGES = {
    "python", "javascript", "typescript", "java", "cpp", "c", "csharp", "go", 
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css"
}
MAX_PROMPT_LENGTH = 5000


class CodeRequest(BaseModel):
    language: str = Field(..., description="Programming language for code generation")
    prompt: str = Field(..., max_length=MAX_PROMPT_LENGTH, description="Code generation prompt")
    
    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v.lower() not in ALLOWED_LANGUAGES:
            raise ValueError(f"Unsupported language: {v}. Allowed: {', '.join(sorted(ALLOWED_LANGUAGES))}")
        return v.lower()
    
    @field_validator("prompt")
    @classmethod
    def validate_prompt_field(cls, v: str) -> str:
        # Use the centralized prompt validator
        return validate_prompt(v)


def run_coder_chain(*, language: str, prompt: str) -> str:
    """Blocking helper that invokes the coder chain."""
    return coder_chain.invoke({
        "language": language,
        "prompt": prompt,
    })


@app.post("/coder/generate")
@limiter.limit("10/minute")
async def coder_generate(request: Request, req: CodeRequest) -> dict:
    """Generate code using Qwen3 Coder based on natural language prompt."""
    try:
        code = await run_in_threadpool(
            run_coder_chain,
            language=req.language,
            prompt=req.prompt,
        )
        return {"code": code}
    except ValueError as e:
        logger.warning("Invalid request for code generation: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to generate code for language %s", req.language)
        raise HTTPException(status_code=500, detail="Code generation failed")
