#!/bin/bash

# Ensure services are running script
# This script ensures all required services are running

echo "Checking and ensuring all services are running..."

# Check and start supervisor if not running
if ! pgrep supervisord > /dev/null; then
    echo "Starting supervisord..."
    supervisord -c /etc/supervisor/supervisord.conf
    sleep 2
fi

# Check and restart services if needed
for service in mongodb backend frontend; do
    status=$(supervisorctl status $service | awk '{print $2}')
    if [ "$status" != "RUNNING" ]; then
        echo "Restarting $service..."
        supervisorctl restart $service
    else
        echo "$service is running"
    fi
done

echo "All services check completed."