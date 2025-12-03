#!/bin/bash
# Fix Google OAuth and Backend Issues in Production

echo "🔧 Fixing B Boutique Production Issues..."

# Stop all containers
echo "📦 Stopping containers..."
cd /path/to/production/b_boutique/backend
docker-compose -f docker-compose.prod.yml down

# Remove old database volume (THIS WILL DELETE DATA - backup first if needed!)
echo "⚠️  WARNING: This will remove the database volume!"
read -p "Have you backed up your data? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted. Please backup your data first."
    exit 1
fi

docker volume rm backend_postgres_data

# Rebuild and start containers with new configuration
echo "🏗️  Rebuilding containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check backend logs
echo "📋 Backend logs:"
docker-compose -f docker-compose.prod.yml logs backend --tail=50

# Check backend health
echo "🏥 Checking backend health..."
docker-compose -f docker-compose.prod.yml exec backend curl -f http://localhost:8000/api/v1/health || echo "❌ Backend not healthy"

echo "✅ Done! Check the logs above for any errors."
echo ""
echo "🔍 To monitor logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "🔍 To check status: docker-compose -f docker-compose.prod.yml ps"
