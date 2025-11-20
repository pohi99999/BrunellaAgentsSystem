
import os
import pathlib
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from specialists.coder_agent import coder_chain

# Define the FastAPI app
app = FastAPI(title="Brunella Agent Server")

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

# The langgraph dev server will automatically discover and serve the graphs
# defined in langgraph.json. We don't need to manually add the routes here.

# The frontend serving is temporarily removed for debugging.


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
    def validate_prompt(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


logger = logging.getLogger(__name__)


def run_coder_chain(*, language: str, prompt: str) -> str:
    """Blocking helper that invokes the coder chain."""
    return coder_chain.invoke({
        "language": language,
        "prompt": prompt,
    })


@app.post("/coder/generate")
async def coder_generate(req: CodeRequest) -> dict:
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

