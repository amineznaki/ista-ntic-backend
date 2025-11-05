#!/usr/bin/env bash
set -e
# Wait a bit for DB (simple approach)
sleep 2
# Create/update admin user with password from ADMIN_PASSWORD env var
python create_admin.py
# Start gunicorn
exec gunicorn --bind 0.0.0.0:5000 app:app
