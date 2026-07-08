from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import os
import base64
from xray_config import generate_xray_config, get_default_uuid, get_vless_link
from xray_manager import XrayManager

app = FastAPI()
xray_manager = XrayManager()
DEFAULT_UUID = get_default_uuid()

@app.on_event("startup")
async def startup():
    config = generate_xray_config(DEFAULT_UUID)
    xray_manager.start(config)
    print(f"🚀 Server started with UUID: {DEFAULT_UUID}")

@app.on_event("shutdown")
async def shutdown():
    xray_manager.stop()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "uuid": DEFAULT_UUID,
        "links": {
            "xhttp": get_vless_link(DEFAULT_UUID, "xhttp"),
            "ws": get_vless_link(DEFAULT_UUID, "ws")
        }
    }

@app.get("/sub/{uuid}")
async def subscription(uuid: str):
    if uuid != DEFAULT_UUID:
        raise HTTPException(status_code=404)
    
    links = [
        get_vless_link(uuid, "xhttp"),
        get_vless_link(uuid, "ws")
    ]
    content = base64.b64encode("\n".join(links).encode()).decode()
    
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "profile-title": "X4G",
            "support-url": "https://t.me/Farajian2004f",
        }
    )

@app.get("/health")
async def health():
    return {"status": xray_manager.get_status(), "uuid": DEFAULT_UUID}