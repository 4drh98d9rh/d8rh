import os
import uvicorn
from fastapi import FastAPI
from xray_handler import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("xray_handler:app", host="0.0.0.0", port=port)