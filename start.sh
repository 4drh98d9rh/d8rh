#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "  🚀 X4G Xray Server"
echo "═══════════════════════════════════════════════════════════"
echo "  API PORT: 8080"
echo "  XRAY PORT: 8443"
echo "  DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-Not Set}"
echo "═══════════════════════════════════════════════════════════"

/usr/local/bin/xray -version

echo "═══════════════════════════════════════════════════════════"
echo "🚀 Starting application..."

python main.py