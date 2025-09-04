
import sys
import os
import uvicorn

# Add the backend src directory to the Python path
sys.path.insert(0, os.path.abspath('backend/src'))

from app import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
