#!/bin/bash

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Error handling
set -e

echo -e "${GREEN}Starting ULocation-v2 deployment...${NC}"

# Create necessary directories
echo -e "${GREEN}Creating necessary directories...${NC}"
mkdir -p uploads/static uploads/promotions uploads/locations

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo -e "${RED}No .env file found. Please create one based on .env.example${NC}"
  exit 1
fi

# Build and start the containers
echo -e "${GREEN}Building and starting containers...${NC}"
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Configure nginx
echo -e "${GREEN}Configuring NGINX...${NC}"
# Copy NGINX configuration to sites-available (if needed on deployment server)
sudo cp nginx/ulocation.conf /etc/nginx/sites-available/

# Enable the site if it's not already enabled
sudo ln -sf /etc/nginx/sites-available/ulocation.conf /etc/nginx/sites-enabled/

# Test NGINX configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Your application is now available at http://64.23.174.176/ulocation/${NC}"
