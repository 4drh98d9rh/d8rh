from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import os
import base64
import logging
import sys
from xray_config import generate_xray_config, get_default_uuid, get_vless_link, get_domain
from xray_manager import XrayManager

# Setup logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()
xray_manager = XrayManager()
DEFAULT_UUID = get_default_uuid()
DOMAIN = get_domain()

# Log startup info
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
        logger.info("📝 Config generated, starting Xray...")
        result = xray_manager.start(config)
        if result:
            logger.info(f"✅ Xray started successfully with PID: {result.pid}")
        else:
            logger.error("❌ Failed to start Xray")
            # Try to install and start again with more logging
            logger.info("🔄 Retrying Xray installation...")
            xray_manager.xray_path = None
            result = xray_manager.start(config)
            if result:
                logger.info(f"✅ Xray started successfully on retry (PID: {result.pid})")
            else:
                logger.error("❌ Xray startup failed after retry")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Shutting down...")
    xray_manager.stop()

@app.get("/")
async def root():
    status = xray_manager.get_status()
    logger.info(f"📊 Status check: {status}")
    return {
        "status": "ok",
        "domain": DOMAIN,
        "uuid": DEFAULT_UUID,
        "links": {
            "xhttp": get_vless_link(DEFAULT_UUID, "xhttp"),
            "ws": get_vless_link(DEFAULT_UUID, "ws")
        },
        "xray_status": status,
        "xray_pid": xray_manager.get_pid()
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
    status = xray_manager.get_status()
    return {
        "status": "healthy" if status == "running" else "degraded",
        "domain": DOMAIN,
        "xray": status,
        "pid": xray_manager.get_pid()
    }

@app.get("/debug")
async def debug():
    """Debug endpoint to check environment and Xray status"""
    import socket
    
    # Check ports
    ports_status = {}
    for port in [8443, 8444]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('0.0.0.0', port))
            sock.close()
            ports_status[port] = "listening" if result == 0 else "not listening"
        except:
            ports_status[port] = "error"
    
    return {
        "domain": DOMAIN,
        "uuid": DEFAULT_UUID,
        "xray_status": xray_manager.get_status(),
        "xray_pid": xray_manager.get_pid(),
        "xray_path": xray_manager.xray_path,
        "ports": ports_status,
        "environment": {
            "RAILWAY_PUBLIC_DOMAIN": os.environ.get("RAILWAY_PUBLIC_DOMAIN", "NOT SET"),
            "PORT": os.environ.get("PORT", "NOT SET"),
        }
    }