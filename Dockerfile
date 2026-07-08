FROM python:3.11-slim

WORKDIR /app

# Install dependencies including Xray
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install Xray directly in Docker
RUN wget -qO- https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip > /tmp/xray.zip \
    && unzip -q /tmp/xray.zip -d /usr/local/bin/ \
    && rm /tmp/xray.zip \
    && chmod +x /usr/local/bin/xray

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["./start.sh"]