#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "  🚀 X4G Xray Server"
echo "═══════════════════════════════════════════════════════════"
echo "  PORT: ${PORT:-8000}"
echo "  DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-Not Set}"
echo "═══════════════════════════════════════════════════════════"

/usr/local/bin/xray -version

python main.py