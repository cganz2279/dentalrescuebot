#!/bin/bash

# Permanent fix for .env file reverting to wrong URL
CORRECT_URL="https://dentist-portal-3.emergent.host"
ENV_FILE="/app/frontend/.env"
BACKUP_FILE="/app/frontend/.env.backup"

echo "Fixing frontend .env file permanently..."

# Fix main .env file
cat > "$ENV_FILE" << EOF
REACT_APP_BACKEND_URL=$CORRECT_URL
WDS_SOCKET_PORT=443
EOF

# Fix backup file
cat > "$BACKUP_FILE" << EOF
REACT_APP_BACKEND_URL=$CORRECT_URL
WDS_SOCKET_PORT=443
EOF

echo "✅ Fixed both .env and .env.backup files"
echo "✅ Set REACT_APP_BACKEND_URL to: $CORRECT_URL"

# Make files readonly to prevent accidental overwrites
chmod 444 "$ENV_FILE"
chmod 444 "$BACKUP_FILE"

echo "✅ Made files readonly to prevent overwrites"
echo "✅ Permanent fix applied!"