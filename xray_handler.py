from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import os
import base64
import logging
from xray_config import generate_xray_config, get_default_uuid, get_vless_link, get_domain
from xray_manager import XrayManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
xray_manager = XrayManager()
DEFAULT_UUID = get_default_uuid()
DOMAIN = get_domain()

# Log startup info
logger.info(f"🌐 Domain detected: {DOMAIN}")
logger.info(f"🔑 UUID: {DEFAULT_UUID}")

@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting application...")
    config = generate_xray_config(DEFAULT_UUID)
    xray_manager.start(config)
    logger.info(f"✅ Server ready with domain: {DOMAIN}")

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Shutting down...")
    xray_manager.stop()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "domain": DOMAIN,
        "uuid": DEFAULT_UUID,
        "links": {
            "xhttp": get_vless_link(DEFAULT_UUID, "xhttp"),
            "ws": get_vless_link(DEFAULT_UUID, "ws")
        },
        "xray_status": xray_manager.get_status()
    }

@app.get("/sub/{uuid}")
async def subscription(uuid: str):
    if uuid != DEFAULT_UUID:
        raise HTTPException(status_code=404, detail="Invalid UUID")
    
    links = [
        get_vless_link(uuid, "xhttp"),
        get_vless_link(uuid, "ws")
    ]
    content = base64.b64encode("\n".join(links).encode()).decode()
    
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "profile-title": "X4G Xray",
            "profile-update-interval": "24",
            "support-url": "https://t.me/Farajian2004f",
        }
    )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "domain": DOMAIN,
        "xray": xray_manager.get_status(),
        "pid": xray_manager.get_pid()
    }

@app.get("/debug")
async def debug():
    """Debug endpoint to check environment variables"""
    return {
        "domain": DOMAIN,
        "railway_domain": os.environ.get("RAILWAY_PUBLIC_DOMAIN", "NOT SET"),
        "all_env": {k: v for k, v in os.environ.items() if not k.startswith("SECRET")}
    }