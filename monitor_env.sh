#!/bin/bash

# Monitor and auto-fix .env file
CORRECT_URL="https://dentist-portal-3.emergent.host"
ENV_FILE="/app/frontend/.env"

while true; do
    current_url=$(grep "REACT_APP_BACKEND_URL" "$ENV_FILE" | cut -d'=' -f2)
    
    if [ "$current_url" != "$CORRECT_URL" ]; then
        echo "$(date): ⚠️  Detected wrong URL: $current_url"
        echo "$(date): 🔧 Fixing to correct URL: $CORRECT_URL"
        
        # Fix the file
        chmod 644 "$ENV_FILE"
        cat > "$ENV_FILE" << EOF
REACT_APP_BACKEND_URL=$CORRECT_URL
WDS_SOCKET_PORT=443
EOF
        chmod 444 "$ENV_FILE"
        
        echo "$(date): ✅ Fixed .env file"
        
        # Restart frontend to apply changes
        sudo supervisorctl restart frontend
        echo "$(date): ✅ Restarted frontend service"
    fi
    
    sleep 30  # Check every 30 seconds
done