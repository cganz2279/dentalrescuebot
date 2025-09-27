#!/bin/bash

# Container startup script to ensure all services start properly

echo "Starting container services..."

# Start supervisord if not running
if ! pgrep supervisord > /dev/null; then
    echo "Starting supervisord..."
    supervisord -c /etc/supervisor/supervisord.conf &
    sleep 3
fi

# Start cron if not running
if ! pgrep cron > /dev/null; then
    echo "Starting cron..."
    service cron start
fi

# Ensure all services are running
/app/ensure_services.sh

# Set up cron job if not exists
if ! crontab -l 2>/dev/null | grep -q "ensure_services.sh"; then
    echo "*/5 * * * * /app/ensure_services.sh >> /var/log/service_monitor.log 2>&1" | crontab -
    echo "Service monitoring cron job added"
fi

echo "Container startup complete. All services should be running."