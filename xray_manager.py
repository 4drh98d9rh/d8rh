import subprocess
import os
import json
import time
import urllib.request
import zipfile
import stat
import logging

logger = logging.getLogger(__name__)

class XrayManager:
    def __init__(self):
        self.process = None
        self.config_path = "/tmp/xray-config.json"
        self.xray_path = self._find_xray()
        self.started = False
    
    def _find_xray(self):
        paths = [
            "./xray",
            "/usr/local/bin/xray",
            "/usr/bin/xray",
            "/app/xray",
            "/tmp/xray",
            "/usr/bin/xray-core/xray"
        ]
        for p in paths:
            if os.path.exists(p) and os.access(p, os.X_OK):
                logger.info(f"✅ Found Xray at: {p}")
                return p
        
        # Try which command
        try:
            import shutil
            which_xray = shutil.which("xray")
            if which_xray:
                logger.info(f"✅ Found Xray via which: {which_xray}")
                return which_xray
        except:
            pass
        
        logger.warning("⚠️ Xray not found")
        return None
    
    def install_xray(self):
        logger.info("📦 Installing Xray-core...")
        try:
            # Create temp directory
            os.makedirs("/tmp", exist_ok=True)
            
            # Download Xray
            url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"
            logger.info(f"⬇️ Downloading from: {url}")
            urllib.request.urlretrieve(url, "/tmp/xray.zip")
            
            # Extract
            logger.info("📂 Extracting...")
            with zipfile.ZipFile("/tmp/xray.zip", 'r') as z:
                z.extractall("/tmp")
            
            # Move to current directory
            if os.path.exists("/tmp/xray"):
                os.rename("/tmp/xray", "./xray")
                os.chmod("./xray", 0o755)
                logger.info("✅ Xray installed to ./xray")
                
                # Cleanup
                os.remove("/tmp/xray.zip")
                return "./xray"
            else:
                # Try alternative location
                if os.path.exists("/tmp/xray.exe"):
                    os.rename("/tmp/xray.exe", "./xray")
                    os.chmod("./xray", 0o755)
                    os.remove("/tmp/xray.zip")
                    return "./xray"
            
            logger.error("❌ Xray binary not found after extraction")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to install Xray: {e}")
            return None
    
    def start(self, config):
        try:
            # Save config
            logger.info("💾 Saving config...")
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Find or install Xray
            if not self.xray_path or not os.path.exists(self.xray_path):
                logger.info("🔧 Xray not found, installing...")
                self.xray_path = self.install_xray()
            
            if not self.xray_path or not os.path.exists(self.xray_path):
                logger.error("❌ Xray installation failed")
                return None
            
            # Make sure it's executable
            os.chmod(self.xray_path, 0o755)
            
            # Check if it's running already
            if self.process and self.process.poll() is None:
                logger.warning("⚠️ Xray already running")
                return self.process
            
            # Start Xray
            cmd = [self.xray_path, "-config", self.config_path]
            logger.info(f"🚀 Starting Xray: {' '.join(cmd)}")
            
            # Create log files
            with open("/tmp/xray.log", "w") as log_file:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=log_file,
                    stderr=log_file,
                    text=True
                )
            
            # Wait for startup
            time.sleep(3)
            
            # Check if running
            if self.process.poll() is not None:
                # Read log
                try:
                    with open("/tmp/xray.log", "r") as f:
                        log_content = f.read()
                    logger.error(f"❌ Xray failed to start. Log: {log_content}")
                except:
                    pass
                return None
            
            self.started = True
            logger.info(f"✅ Xray started successfully (PID: {self.process.pid})")
            
            # Check if port is listening
            time.sleep(1)
            self._check_ports()
            
            return self.process
            
        except Exception as e:
            logger.error(f"❌ Error starting Xray: {e}")
            return None
    
    def _check_ports(self):
        """Check if Xray ports are listening"""
        import socket
        ports = [8443, 8444]
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('0.0.0.0', port))
                sock.close()
                if result == 0:
                    logger.info(f"✅ Port {port} is listening")
                else:
                    logger.warning(f"⚠️ Port {port} is not listening")
            except:
                pass
    
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
        elif self.process:
            return f"stopped (exit code: {self.process.poll()})"
        else:
            # Check if it might be running but we lost the process
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('0.0.0.0', 8443))
                sock.close()
                if result == 0:
                    return "running (detected on port 8443)"
            except:
                pass
            return "not started"
    
    def get_pid(self):
        if self.process and self.process.poll() is None:
            return self.process.pid
        return None