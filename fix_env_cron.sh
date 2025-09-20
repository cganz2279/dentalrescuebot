#!/bin/bash
# Cron job to fix .env file every minute

CORRECT_URL="https://dentist-portal-3.emergent.host"
ENV_FILE="/app/frontend/.env"

# Check if .env has wrong URL
if grep -q "dental-pdf-sync.preview.emergentagent.com" "$ENV_FILE"; then
    echo "$(date): FIXING .env file - wrong URL detected" >> /var/log/env_cron.log
    
    # Fix the file
    cat > "$ENV_FILE" << EOL
REACT_APP_BACKEND_URL=$CORRECT_URL
WDS_SOCKET_PORT=443
EOL
    
    # Restart frontend
    sudo supervisorctl restart frontend
    echo "$(date): .env file fixed and frontend restarted" >> /var/log/env_cron.log
fi
