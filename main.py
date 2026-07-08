import os
import uvicorn
from xray_handler import app

if __name__ == "__main__":
    port = 8080  # پورت ثابت 8080 برای API
    uvicorn.run("xray_handler:app", host="0.0.0.0", port=port)