
import pathlib
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from specialists.coder_agent import coder_chain
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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


@app.post("/coder/generate")
def coder_generate(req: CodeRequest) -> dict:
    try:
        code = coder_chain.invoke({
            "language": req.language,
            "prompt": req.prompt,
        })
        return {"code": code}
    except Exception as e:
        return {"error": str(e)}

