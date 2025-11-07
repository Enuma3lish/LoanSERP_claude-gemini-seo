#!/bin/bash
# Start Django backend server

# Change to backend directory
cd "$(dirname "$0")/backend"

# Load environment variables
export $(cat ../.env | grep -v '^#' | xargs)

echo "========================================="
echo "Starting Django Backend Server"
echo "========================================="
echo "Server will run on: http://localhost:8000"
echo "API endpoints available at: http://localhost:8000/api/"
echo ""

# Run migrations first
echo "Running database migrations..."
python manage.py migrate

# Start Django development server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
