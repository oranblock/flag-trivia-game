#!/bin/bash

# deploy.sh - Script to deploy flag game with nginx and make it publicly accessible

# Exit on error
set -e

echo "=== Flag Game Deployment Script ==="
echo "This script will deploy the flag game using Nginx and Gunicorn"

# Install dependencies if not already installed
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y nginx python3-pip python3-venv

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create Nginx configuration
echo "Setting up Nginx configuration..."
sudo tee /etc/nginx/sites-available/flag-game.conf > /dev/null << 'EOL'
server {
    listen 8080;  # Using port 8080 instead of 80 to avoid permission issues
    server_name _;  # This will match any domain name

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/clouduser/game/static;
        expires 30d;
    }
}
EOL

# Enable the site
echo "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/flag-game.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test Nginx config
echo "Testing Nginx configuration..."
sudo nginx -t

# Check if we're running with systemd
if command -v systemctl >/dev/null 2>&1; then
    echo "System uses systemd, restarting Nginx..."
    sudo systemctl restart nginx
else
    echo "System doesn't use systemd, manually starting Nginx..."
    sudo service nginx restart || sudo nginx -s reload || sudo nginx
fi

# Create a start script for gunicorn
echo "Creating start script..."
cat > start_game.sh << 'EOL'
#!/bin/bash
cd /home/clouduser/game
source venv/bin/activate
gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
EOL

chmod +x start_game.sh

# Create a supervisor conf file if available
if command -v supervisorctl >/dev/null 2>&1; then
    echo "Configuring supervisor..."
    sudo tee /etc/supervisor/conf.d/flag-game.conf > /dev/null << 'EOL'
[program:flag-game]
command=/home/clouduser/game/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
directory=/home/clouduser/game
user=clouduser
autostart=true
autorestart=true
redirect_stderr=true
EOL
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start flag-game
fi

# Start the application manually if supervisor is not available
echo "Starting the application..."
echo "Starting gunicorn in the background..."
cd /home/clouduser/game
source venv/bin/activate
nohup gunicorn --workers 3 --bind 127.0.0.1:8000 app:app > gunicorn.log 2>&1 &
APP_PID=$!
echo "Application started with PID $APP_PID"
echo $APP_PID > app.pid
cd - > /dev/null

# Get public IP address
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "localhost")

echo "=== Deployment Complete ==="
echo "Your flag game is now running and should be accessible at:"
echo "http://$PUBLIC_IP:8080"
echo ""
echo "If you're using a cloud service, make sure port 8080 is open in your security group/firewall."
echo "To stop the application, run: kill \$(cat /home/clouduser/game/app.pid)"
echo "To restart the application, run: ./start_game.sh"
echo ""
echo "The application is also running in the background with nohup. To view the logs:"
echo "tail -f /home/clouduser/game/gunicorn.log"