#!/bin/bash

# Script to print public IP address

echo "Fetching your public IP address..."

# Try multiple services in case one fails
PUBLIC_IP=$(curl -s https://api.ipify.org || \
            curl -s https://ifconfig.me || \
            curl -s https://icanhazip.com || \
            curl -s https://checkip.amazonaws.com || \
            curl -s https://ipinfo.io/ip)

if [ -n "$PUBLIC_IP" ]; then
    echo "Your public IP address is: $PUBLIC_IP"
    echo "Your flag game should be accessible at: http://$PUBLIC_IP:8000"
else
    echo "Could not determine your public IP address."
    echo "Check your internet connection or try manually at https://whatismyip.com"
fi