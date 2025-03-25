# ULocation-v2 Deployment Guide

This document provides instructions for deploying the ULocation-v2 project to a DigitalOcean droplet.

## Prerequisites

- Docker and Docker Compose installed on the server
- NGINX installed and configured
- Git installed

## Deployment Steps

1. **Clone the repository**

```bash
mkdir -p /home/projects
cd /home/projects
git clone <your-repository-url> ulocation-v2
cd ulocation-v2
```

2. **Create environment file**

```bash
cp .env.example .env
# Edit the .env file with appropriate values
nano .env
```

3. **Configure NGINX**

```bash
# Copy the NGINX configuration file
sudo cp nginx/ulocation.conf /etc/nginx/sites-available/

# Create a symbolic link to enable the site
sudo ln -sf /etc/nginx/sites-available/ulocation.conf /etc/nginx/sites-enabled/

# Test the NGINX configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx
```

4. **Run the deployment script**

```bash
chmod +x deploy.sh
./deploy.sh
```

5. **Verify deployment**

Check that all services are running:

```bash
docker-compose -f docker-compose.prod.yml ps
```

Access your application at: http://64.23.174.176/ulocation/

## Troubleshooting

- **Check logs**: `docker-compose -f docker-compose.prod.yml logs -f [service_name]`
- **Restart services**: `docker-compose -f docker-compose.prod.yml restart [service_name]`
- **Check NGINX status**: `sudo systemctl status nginx`

## Updates

To update the application:

```bash
cd /home/projects/ulocation-v2
git pull
./deploy.sh
```

## Backup

To backup the MongoDB data:

```bash
# Create a backup directory
mkdir -p /backups/ulocation

# Backup MongoDB data
docker-compose -f docker-compose.prod.yml exec -T mongodb mongodump --archive > /backups/ulocation/mongo-$(date +%Y%m%d%H%M%S).archive
```
