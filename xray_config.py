import json
import os
import hashlib
import secrets

def get_domain():
    """Get domain from environment variables"""
    domain = (
        os.environ.get("RAILWAY_PUBLIC_DOMAIN") or
        os.environ.get("RAILWAY_STATIC_URL") or
        os.environ.get("RENDER_EXTERNAL_HOSTNAME") or
        "localhost"
    )
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    return domain

def generate_xray_config(uuid):
    host = get_domain()
    port = int(os.environ.get("PORT", 8000))
    
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "listen": "0.0.0.0",
                "port": port,  # استفاده از پورت 8000
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": uuid}],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "xhttp",
                    "security": "none",
                    "xhttpSettings": {
                        "path": "/xhttp",
                        "host": host
                    }
                }
            },
            {
                "listen": "0.0.0.0",
                "port": port,  # استفاده از پورت 8000
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": uuid}],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {"path": "/ws"}
                }
            }
        ],
        "outbounds": [{"protocol": "freedom"}]
    }
    return config

def get_default_uuid():
    secret = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))
    uid = hashlib.sha256(f"default{secret}".encode()).hexdigest()
    return f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:32]}"

def get_vless_link(uuid, protocol="xhttp"):
    host = get_domain()
    port = os.environ.get("PORT", "8000")  # استفاده از پورت 8000
    path = "/xhttp" if protocol == "xhttp" else "/ws"
    
    return f"vless://{uuid}@{host}:{port}?encryption=none&type={protocol}&path={path}&host={host}&security=none#X4G-{protocol.upper()}"