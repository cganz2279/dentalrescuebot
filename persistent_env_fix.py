#!/usr/bin/env python3
"""
Persistent environment variable fixer - runs in background to prevent .env file reversion
"""

import time
import os
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

CORRECT_URL = "https://dentist-portal-3.emergent.host"
WRONG_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
ENV_FILE = "/app/frontend/.env"
BACKUP_FILE = "/app/frontend/.env.backup"

def fix_env_file():
    """Fix the .env file with correct URL"""
    try:
        # Make file writable
        os.chmod(ENV_FILE, 0o644)
        
        # Write correct content
        with open(ENV_FILE, 'w') as f:
            f.write(f"REACT_APP_BACKEND_URL={CORRECT_URL}\n")
            f.write("WDS_SOCKET_PORT=443\n")
        
        # Also fix backup file
        with open(BACKUP_FILE, 'w') as f:
            f.write(f"REACT_APP_BACKEND_URL={CORRECT_URL}\n")
            f.write("WDS_SOCKET_PORT=443\n")
        
        logger.info(f"✅ Fixed .env files with correct URL: {CORRECT_URL}")
        
        # Restart frontend to apply changes
        subprocess.run(['sudo', 'supervisorctl', 'restart', 'frontend'], 
                      capture_output=True, text=True)
        logger.info("✅ Restarted frontend service")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to fix .env file: {e}")
        return False

def monitor_and_fix():
    """Monitor .env file and fix if it gets corrupted"""
    logger.info("🔍 Starting persistent .env monitor...")
    
    while True:
        try:
            # Read current .env file
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    content = f.read()
                
                # Check if it has the wrong URL
                if WRONG_URL in content:
                    logger.warning(f"⚠️ Detected wrong URL in .env file!")
                    logger.info(f"🔧 Fixing .env file...")
                    fix_env_file()
                elif CORRECT_URL not in content:
                    logger.warning(f"⚠️ .env file missing correct URL!")
                    logger.info(f"🔧 Fixing .env file...")
                    fix_env_file()
                # else:
                #     logger.info(f"✅ .env file is correct")
            else:
                logger.warning(f"⚠️ .env file missing!")
                fix_env_file()
                
        except Exception as e:
            logger.error(f"❌ Monitor error: {e}")
        
        # Wait 30 seconds before next check
        time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_and_fix()
    except KeyboardInterrupt:
        logger.info("🛑 Monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitor crashed: {e}")