#!/bin/bash
set -e

echo "=========================================="
echo "B Boutique Production Deployment Script"
echo "=========================================="
echo ""

# Configuration
DOMAIN="benedettoboutique.com"
EMAIL="claytonsiby@gmail.com"  # Your email for Let's Encrypt notifications

echo "Step 1: Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }
echo "✓ Docker and Docker Compose are installed"
echo ""

echo "Step 2: Creating necessary directories..."
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p nginx
echo "✓ Directories created"
echo ""

echo "Step 3: Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true
echo "✓ Stopped existing containers"
echo ""

echo "Step 4: Building and starting services (without SSL first)..."
docker-compose -f docker-compose.prod.yml up -d redis backend celery_worker frontend
echo "✓ Core services started"
echo ""

echo "Step 5: Waiting for services to be healthy..."
sleep 30
echo "✓ Services should be ready"
echo ""

echo "Step 6: Obtaining SSL certificate from Let's Encrypt..."
echo "NOTE: Make sure your DNS A record for $DOMAIN points to this server's IP!"
read -p "Press Enter to continue once DNS is configured..."

# Initial certificate request
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo "✓ SSL certificate obtained"
echo ""

echo "Step 7: Starting Nginx and Certbot..."
docker-compose -f docker-compose.prod.yml up -d nginx certbot
echo "✓ Nginx and Certbot started"
echo ""

echo "Step 8: Verifying deployment..."
docker-compose -f docker-compose.prod.yml ps
echo ""

echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your application should now be available at:"
echo "  https://$DOMAIN"
echo ""
echo "Backend API documentation:"
echo "  https://$DOMAIN/docs"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f [service_name]"
echo ""
echo "To restart services:"
echo "  docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""
echo "SSL certificates will auto-renew every 12 hours."
echo "=========================================="
