
import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Define the FastAPI app
app = FastAPI(title="Brunella Agent Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The langgraph dev server will automatically discover and serve the graphs
# defined in langgraph.json. We don't need to manually add the routes here.

# The frontend serving is temporarily removed for debugging.

