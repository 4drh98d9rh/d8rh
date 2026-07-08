import json
import os
import hashlib
import secrets

def generate_xray_config(uuid):
    # دامنه خودکار از Railway گرفته میشه
    host = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost")
    
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
    host = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost")
    port = "8443" if protocol == "xhttp" else "8444"
    path = "/xhttp" if protocol == "xhttp" else "/ws"
    
    return f"vless://{uuid}@{host}:{port}?encryption=none&security=tls&type={protocol}&path={path}&host={host}#X4G-{protocol.upper()}"