FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget unzip psmisc \
    && rm -rf /var/lib/apt/lists/* \
    && wget -qO- https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip > /tmp/xray.zip \
    && unzip -q /tmp/xray.zip -d /usr/local/bin/ \
    && rm /tmp/xray.zip \
    && chmod +x /usr/local/bin/xray

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 8080 8443

CMD ["./start.sh"]