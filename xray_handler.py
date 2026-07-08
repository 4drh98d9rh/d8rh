from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import os
import base64
import logging
import sys
from xray_config import generate_xray_config, get_default_uuid, get_vless_link, get_domain
from xray_manager import XrayManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()
xray_manager = XrayManager()
DEFAULT_UUID = get_default_uuid()
DOMAIN = get_domain()

logger.info("=" * 50)
logger.info("🚀 X4G Xray Server Starting...")
logger.info(f"🌐 Domain detected: {DOMAIN}")
logger.info(f"🔑 UUID: {DEFAULT_UUID}")
logger.info("=" * 50)

@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting application...")
    try:
        config = generate_xray_config(DEFAULT_UUID)
        result = xray_manager.start(config)
        if result:
            logger.info(f"✅ Xray started successfully with PID: {result.pid}")
        else:
            logger.error("❌ Failed to start Xray")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)

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
        }
    )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "xray": xray_manager.get_status()
    }