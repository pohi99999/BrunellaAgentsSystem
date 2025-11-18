
import pathlib
import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from specialists.coder_agent import coder_chain

# Define the FastAPI app
app = FastAPI(title="Brunella Agent Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # Allow frontend origins (dev and docker-served)
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


class CodeRequest(BaseModel):
    language: str
    prompt: str


logger = logging.getLogger(__name__)


def run_coder_chain(*, language: str, prompt: str) -> str:
    """Blocking helper that invokes the coder chain."""
    return coder_chain.invoke({
        "language": language,
        "prompt": prompt,
    })


@app.post("/coder/generate")
async def coder_generate(req: CodeRequest) -> dict:
    try:
        code = await run_in_threadpool(
            run_coder_chain,
            language=req.language,
            prompt=req.prompt,
        )
        return {"code": code}
    except Exception as e:
        logger.exception("Failed to generate code for language %s", req.language)
        return {"error": str(e)}

