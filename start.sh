#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "  🚀 X4G Xray Server"
echo "═══════════════════════════════════════════════════════════"
echo "  PORT: ${PORT:-8000}"
echo "  DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-Not Set}"
echo "  XRAY_PATH: /usr/local/bin/xray"
echo "═══════════════════════════════════════════════════════════"

# Verify Xray is installed
if [ -f "/usr/local/bin/xray" ]; then
    echo "✅ Xray found at /usr/local/bin/xray"
    /usr/local/bin/xray -version
else
    echo "⚠️ Xray not found, installing..."
    wget -qO- https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip > /tmp/xray.zip
    unzip -q /tmp/xray.zip -d /usr/local/bin/
    rm /tmp/xray.zip
    chmod +x /usr/local/bin/xray
    echo "✅ Xray installed"
fi

echo "═══════════════════════════════════════════════════════════"
echo "🚀 Starting application..."
python main.py