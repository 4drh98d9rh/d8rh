import json
import os
import hashlib
import secrets

def get_domain():
    domain = (
        os.environ.get("RAILWAY_PUBLIC_DOMAIN") or
        os.environ.get("RAILWAY_STATIC_URL") or
        "localhost"
    )
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    return domain

def generate_xray_config(uuid):
    host = get_domain()
    
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "listen": "0.0.0.0",
                "port": 8443,  # فقط یک پورت
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": uuid}],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "xhttp",  # پیش‌فرض XHTTP
                    "security": "none",
                    "xhttpSettings": {
                        "path": "/xhttp",
                        "host": host
                    }
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"]
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
    port = "8443"  # فقط یک پورت
    
    if protocol == "xhttp":
        return f"vless://{uuid}@{host}:{port}?encryption=none&type=xhttp&path=/xhttp&host={host}&security=none#X4G-XHTTP"
    elif protocol == "ws":
        return f"vless://{uuid}@{host}:{port}?encryption=none&type=ws&path=/ws&host={host}&security=none#X4G-WS"
    return None