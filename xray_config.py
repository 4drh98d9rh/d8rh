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
        os.environ.get("VERCEL_URL") or
        os.environ.get("HEROKU_APP_NAME") and f"{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com" or
        os.environ.get("KOYEB_APP_NAME") and f"{os.environ.get('KOYEB_APP_NAME')}.koyeb.app" or
        os.environ.get("FLY_APP_NAME") and f"{os.environ.get('FLY_APP_NAME')}.fly.dev" or
        "localhost"
    )
    # Clean domain
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    return domain

def generate_xray_config(uuid):
    host = get_domain()
    
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "listen": "0.0.0.0",
                "port": 8443,
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": uuid}],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "xhttp",
                    "security": "tls",
                    "xhttpSettings": {
                        "path": "/xhttp",
                        "host": host
                    },
                    "tlsSettings": {"allowInsecure": True}
                }
            },
            {
                "listen": "0.0.0.0",
                "port": 8444,
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": uuid}],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "tls",
                    "wsSettings": {"path": "/ws"},
                    "tlsSettings": {"allowInsecure": True}
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
    port = "8443" if protocol == "xhttp" else "8444"
    path = "/xhttp" if protocol == "xhttp" else "/ws"
    
    return f"vless://{uuid}@{host}:{port}?encryption=none&security=tls&type={protocol}&path={path}&host={host}#X4G-{protocol.upper()}"