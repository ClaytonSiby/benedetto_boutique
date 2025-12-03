#!/bin/bash
# Safe fix - Updates password in existing database

echo "🔧 Safely updating database password in production..."

# Change to backend directory
cd /path/to/production/b_boutique/backend

# Connect to postgres container and update password
echo "🔐 Updating postgres password..."
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -c "ALTER USER bboutique WITH PASSWORD 'BBoutique2024SecureDB!Pass#9821';"

# Restart backend with new credentials
echo "🔄 Restarting backend..."
docker-compose -f docker-compose.prod.yml restart backend

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 20

# Check backend logs
echo "📋 Backend logs:"
docker-compose -f docker-compose.prod.yml logs backend --tail=50

# Test backend health
echo "🏥 Testing backend health..."
curl -f https://benedettoboutique.com/api/v1/health

# Test Google OAuth endpoint
echo "🔍 Testing Google OAuth endpoint..."
curl -I https://benedettoboutique.com/api/v1/auth/google/login

echo "✅ Done! Backend should now be working."
