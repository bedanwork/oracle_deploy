#!/bin/bash
set -e

# Change ownership and permissions
echo "Fixing permissions for Oracle data directory..."
chown -R 54321:54321 /opt/oracle/oradata
chmod -R 775 /opt/oracle/oradata

# Start the Oracle database chmod +x entrypoint.sh
echo "Starting Oracle Database..."
exec /bin/bash -c "$@"
