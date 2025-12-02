#!/bin/bash
set -e

echo "=========================================="
echo "Initial SSL Certificate Setup"
echo "=========================================="
echo ""

DOMAIN="benedettoboutique.com"
EMAIL="claytonsiby@gmail.com"

echo "This script will obtain an SSL certificate for $DOMAIN"
echo ""

# Create directories
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p nginx

# Create temporary nginx config for certificate challenge
cat > nginx/nginx-init.conf << 'EOF'
server {
    listen 80;
    server_name benedettoboutique.com www.benedettoboutique.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Server is running';
        add_header Content-Type text/plain;
    }
}
EOF

echo "Starting temporary Nginx for certificate validation..."
docker run -d --name temp_nginx \
    -p 80:80 \
    -v $(pwd)/nginx/nginx-init.conf:/etc/nginx/conf.d/default.conf:ro \
    -v $(pwd)/certbot/www:/var/www/certbot:ro \
    nginx:alpine

sleep 5

echo "Requesting SSL certificate..."
docker run --rm \
    -v $(pwd)/certbot/conf:/etc/letsencrypt \
    -v $(pwd)/certbot/www:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN \
    -d www.$DOMAIN

echo "Stopping temporary Nginx..."
docker stop temp_nginx
docker rm temp_nginx

echo ""
echo "=========================================="
echo "✓ SSL Certificate obtained successfully!"
echo "=========================================="
echo ""
echo "You can now run the main deployment:"
echo "  ./deploy.sh"
