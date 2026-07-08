#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "  🚀 X4G Xray Server"
echo "═══════════════════════════════════════════════════════════"
echo "  WEB PORT: ${PORT:-8080}"
echo "  XRAY PORTS: 8443 (XHTTP), 8444 (WS)"
echo "  DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-Not Set}"
echo "═══════════════════════════════════════════════════════════"

# نمایش نسخه Xray
/usr/local/bin/xray -version

echo "═══════════════════════════════════════════════════════════"
echo "🚀 Starting application..."

# اجرا در foreground
python main.py