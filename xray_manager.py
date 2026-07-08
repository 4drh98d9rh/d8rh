import subprocess
import os
import json
import time
import urllib.request
import zipfile
import stat

class XrayManager:
    def __init__(self):
        self.process = None
        self.config_path = "/tmp/xray-config.json"
        self.xray_path = self._find_xray()
    
    def _find_xray(self):
        paths = [
            "./xray",
            "/usr/local/bin/xray",
            "/usr/bin/xray",
            "/app/xray",
            "/tmp/xray"
        ]
        for p in paths:
            if os.path.exists(p) and os.access(p, os.X_OK):
                return p
        return None
    
    def install_xray(self):
        print("📦 Installing Xray-core...")
        try:
            # Download Xray
            url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"
            urllib.request.urlretrieve(url, "/tmp/xray.zip")
            
            # Extract
            with zipfile.ZipFile("/tmp/xray.zip, 'r") as z:
                z.extractall("/tmp")
            
            # Move and make executable
            os.rename("/tmp/xray", "./xray")
            os.chmod("./xray", stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            # Cleanup
            os.remove("/tmp/xray.zip")
            
            print("✅ Xray installed successfully")
            return "./xray"
            
        except Exception as e:
            print(f"❌ Failed to install Xray: {e}")
            return None
    
    def start(self, config):
        try:
            # Save config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Install Xray if not found
            if not self.xray_path or not os.path.exists(self.xray_path):
                print("🔧 Xray not found, installing...")
                self.xray_path = self.install_xray()
            
            if not self.xray_path:
                print("❌ Xray installation failed")
                return None
            
            # Start Xray
            print(f"🚀 Starting Xray: {self.xray_path}")
            self.process = subprocess.Popen(
                [self.xray_path, "-config", self.config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(3)
            
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                print(f"❌ Xray failed to start: {stderr}")
                return None
            
            print(f"✅ Xray started (PID: {self.process.pid})")
            return self.process
            
        except Exception as e:
            print(f"❌ Error starting Xray: {e}")
            return None
    
    def stop(self):
        if self.process:
            try:
                print("🛑 Stopping Xray...")
                self.process.terminate()
                time.sleep(2)
                if self.process.poll() is None:
                    self.process.kill()
                self.process = None
                print("✅ Xray stopped")
            except Exception as e:
                print(f"❌ Error stopping Xray: {e}")
    
    def get_status(self):
        if self.process and self.process.poll() is None:
            return "running"
        elif self.process:
            return f"stopped (exit code: {self.process.poll()})"
        return "not started"
    
    def get_pid(self):
        if self.process and self.process.poll() is None:
            return self.process.pid
        return None