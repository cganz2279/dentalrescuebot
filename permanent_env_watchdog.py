#!/usr/bin/env python3
"""
PERMANENT .env file watchdog - Prevents corruption permanently
"""

import time
import os
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - WATCHDOG - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/env_watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CORRECT_URL = "https://dentist-portal-3.emergent.host"
WRONG_URL = "https://dental-portal-fix-1.preview.emergentagent.com"
ENV_FILE = "/app/frontend/.env"
BACKUP_FILE = "/app/frontend/.env.backup"

class EnvFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == ENV_FILE:
            self.check_and_fix_env()
    
    def on_created(self, event):
        if event.src_path == ENV_FILE:
            self.check_and_fix_env()
    
    def check_and_fix_env(self):
        """Check and fix .env file immediately"""
        try:
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    content = f.read()
                
                if WRONG_URL in content or CORRECT_URL not in content:
                    logger.warning("🚨 DETECTED .env CORRUPTION - FIXING IMMEDIATELY")
                    self.fix_env_file()
                else:
                    logger.info("✅ .env file is correct")
        except Exception as e:
            logger.error(f"❌ Error checking .env: {e}")
            self.fix_env_file()
    
    def fix_env_file(self):
        """Fix the .env file with correct URL"""
        try:
            # Make writable
            os.chmod(ENV_FILE, 0o644)
            
            # Write correct content
            with open(ENV_FILE, 'w') as f:
                f.write(f"REACT_APP_BACKEND_URL={CORRECT_URL}\n")
                f.write("WDS_SOCKET_PORT=443\n")
            
            # Also fix backup
            with open(BACKUP_FILE, 'w') as f:
                f.write(f"REACT_APP_BACKEND_URL={CORRECT_URL}\n")
                f.write("WDS_SOCKET_PORT=443\n")
            
            logger.info(f"✅ FIXED .env file with correct URL: {CORRECT_URL}")
            
            # Restart frontend
            subprocess.run(['sudo', 'supervisorctl', 'restart', 'frontend'], 
                          capture_output=True, text=True)
            logger.info("✅ Restarted frontend service")
            
        except Exception as e:
            logger.error(f"❌ Failed to fix .env: {e}")

def main():
    """Main watchdog function"""
    logger.info("🛡️ STARTING PERMANENT .env WATCHDOG SERVICE")
    
    handler = EnvFileHandler()
    
    # Initial check and fix
    handler.check_and_fix_env()
    
    # Set up file system monitoring
    observer = Observer()
    observer.schedule(handler, path='/app/frontend', recursive=False)
    observer.start()
    
    logger.info("👁️ File system monitoring started")
    
    try:
        while True:
            # Also do periodic checks every 10 seconds
            time.sleep(10)
            handler.check_and_fix_env()
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 Watchdog stopped by user")
    except Exception as e:
        logger.error(f"❌ Watchdog error: {e}")
    
    observer.join()

if __name__ == "__main__":
    main()