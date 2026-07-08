import subprocess
import os
import json
import time
import urllib.request
import zipfile

class XrayManager:
    def __init__(self):
        self.process = None
        self.config_path = "/tmp/xray-config.json"
        self.xray_path = self._find_xray()
    
    def _find_xray(self):
        paths = ["./xray", "/usr/local/bin/xray", "/usr/bin/xray"]
        for p in paths:
            if os.path.exists(p):
                return p
        return None
    
    def install_xray(self):
        print("📦 Installing Xray...")
        urllib.request.urlretrieve(
            "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip",
            "/tmp/xray.zip"
        )
        with zipfile.ZipFile("/tmp/xray.zip", 'r') as z:
            z.extractall("/tmp")
        os.rename("/tmp/xray", "./xray")
        os.chmod("./xray", 0o755)
        return "./xray"
    
    def start(self, config):
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        if not self.xray_path:
            self.xray_path = self.install_xray()
        
        self.process = subprocess.Popen(
            [self.xray_path, "-config", self.config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)
        print(f"✅ Xray started (PID: {self.process.pid})")
        return self.process
    
    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
    
    def get_status(self):
        if self.process and self.process.poll() is None:
            return "running"
        return "stopped"