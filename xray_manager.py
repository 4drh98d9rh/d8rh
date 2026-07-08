import subprocess
import os
import json
import time
import logging
import socket

logger = logging.getLogger(__name__)

class XrayManager:
    def __init__(self):
        self.process = None
        self.config_path = "/tmp/xray-config.json"
        self.xray_path = "/usr/local/bin/xray"
        self.started = False
    
    def _check_port(self, port):
        """بررسی اینکه پورت آزاد است یا نه"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('0.0.0.0', port))
            sock.close()
            return result != 0  # True if port is free
        except:
            return False
    
    def start(self, config):
        try:
            # بررسی پورت‌ها
            if not self._check_port(8443):
                logger.warning("⚠️ Port 8443 is in use, killing process...")
                os.system("fuser -k 8443/tcp 2>/dev/null || true")
                time.sleep(2)
            
            if not self._check_port(8444):
                logger.warning("⚠️ Port 8444 is in use, killing process...")
                os.system("fuser -k 8444/tcp 2>/dev/null || true")
                time.sleep(2)
            
            # Save config
            logger.info("💾 Saving config...")
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            if not os.path.exists(self.xray_path):
                logger.error(f"❌ Xray not found at {self.xray_path}")
                return None
            
            if self.process and self.process.poll() is None:
                logger.warning("⚠️ Xray already running")
                return self.process
            
            # Start Xray in background
            cmd = [self.xray_path, "-config", self.config_path]
            logger.info(f"🚀 Starting Xray: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(3)
            
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                error_msg = stderr or stdout or "Unknown error"
                logger.error(f"❌ Xray failed to start: {error_msg}")
                return None
            
            self.started = True
            logger.info(f"✅ Xray started successfully (PID: {self.process.pid})")
            
            # بررسی اینکه پورت‌ها در حال listening هستند
            time.sleep(1)
            if self._check_port(8443):
                logger.warning("⚠️ Port 8443 is not listening!")
            else:
                logger.info("✅ Port 8443 is listening")
                
            if self._check_port(8444):
                logger.warning("⚠️ Port 8444 is not listening!")
            else:
                logger.info("✅ Port 8444 is listening")
            
            return self.process
            
        except Exception as e:
            logger.error(f"❌ Error starting Xray: {e}")
            return None
    
    def stop(self):
        if self.process:
            try:
                logger.info("🛑 Stopping Xray...")
                self.process.terminate()
                time.sleep(2)
                if self.process.poll() is None:
                    self.process.kill()
                self.process = None
                self.started = False
                logger.info("✅ Xray stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping Xray: {e}")
    
    def get_status(self):
        if self.process and self.process.poll() is None:
            return "running"
        return "not started"
    
    def get_pid(self):
        if self.process and self.process.poll() is None:
            return self.process.pid
        return None