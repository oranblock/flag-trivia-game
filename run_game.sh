#!/bin/bash

# run_game.sh - Simple script to run the flag game directly

echo "=== Starting Flag Game ==="

# Check if Python virtual environment exists and create it if not
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Start the application directly with gunicorn
echo "Starting the application with gunicorn..."
echo "The game will be accessible at http://localhost:8000"
echo "Press Ctrl+C to stop the server"
gunicorn --workers 3 --bind 0.0.0.0:8000 app:app