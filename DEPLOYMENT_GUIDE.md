# B Boutique - Production Deployment Guide

## Prerequisites

1. **Domain Configuration**
   - Domain: `benedettoboutique.com`
   - DNS A Record pointing to your VM IP: `130.211.213.48`
   - Also configure `www.benedettoboutique.com` to point to the same IP

2. **Google Cloud OAuth**
   - Update Google Cloud Console OAuth settings:
     - Authorized redirect URIs: `https://benedettoboutique.com/api/v1/auth/google/callback`
     - Authorized JavaScript origins: `https://benedettoboutique.com`

## Deployment Steps

### 1. Transfer Files to VM

From your local machine, sync the project to your VM:

```bash
gcloud compute scp --recurse \
  /Users/claytonsiby/Documents/Github/personal/b_boutique \
  YOUR_VM_NAME:~/ \
  --zone=YOUR_ZONE
```

### 2. SSH into VM

```bash
gcloud compute ssh YOUR_VM_NAME --zone=YOUR_ZONE
```

### 3. Navigate to Project Directory

```bash
cd ~/b_boutique
```

### 4. Make Scripts Executable

```bash
chmod +x deploy.sh setup-ssl.sh
```

### 5. Setup SSL Certificate (First Time Only)

```bash
./setup-ssl.sh
```

This will:
- Create necessary directories
- Start a temporary Nginx server
- Request SSL certificates from Let's Encrypt
- Configure automatic renewal

### 6. Deploy Full Stack

```bash
./deploy.sh
```

This will:
- Build and start all services (PostgreSQL, Redis, Backend, Celery, Frontend, Nginx)
- Configure Nginx with SSL
- Set up automatic certificate renewal

## Post-Deployment

### Verify Services

```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check specific service
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Access Your Application

- **Frontend**: https://benedettoboutique.com
- **Backend API**: https://benedettoboutique.com/api
- **API Docs**: https://benedettoboutique.com/docs

### Create Superuser (if needed)

```bash
docker exec b_boutique_backend python -c "
import sys; sys.path.insert(0, '/app')
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = User(
    username='admin',
    email='admin@benedettoboutique.com',
    password_hash=get_password_hash('YourSecurePassword123'),
    is_active=True,
    is_verified=True,
    is_admin=True
)
db.add(user)
db.commit()
print('Admin created successfully')
db.close()
"
```

## Maintenance Commands

### Restart Services

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Stop Services

```bash
docker-compose -f docker-compose.prod.yml down
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### View SSL Certificate Status

```bash
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates
```

### Manual Certificate Renewal

```bash
docker-compose -f docker-compose.prod.yml exec certbot certbot renew
```

## Troubleshooting

### Certificate Issues

If you get certificate errors:

```bash
# Remove old certificates
sudo rm -rf certbot/conf/*

# Re-run setup
./setup-ssl.sh
```

### DNS Not Propagating

Check DNS propagation:
```bash
dig benedettoboutique.com
nslookup benedettoboutique.com
```

Wait for DNS to propagate (can take up to 48 hours, usually much faster).

### Port Already in Use

```bash
# Check what's using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicting services
sudo systemctl stop apache2  # or nginx, if installed locally
```

### Check Backend Health

```bash
curl http://localhost:8000/api/v1/health
```

### Check Frontend

```bash
curl http://localhost:3000
```

## Security Notes

1. **Environment Variables**: Never commit `.env.production` files to Git
2. **Firewall**: Ensure ports 80 and 443 are open in Google Cloud Firewall
3. **Database**: Consider using a managed PostgreSQL instance for production
4. **Secrets**: Rotate SECRET_KEY and API keys regularly
5. **Backups**: Set up automated database backups

## Architecture

```
Internet
   ↓
Nginx (Port 80/443) - SSL Termination
   ↓
   ├── Frontend (Port 3000) - Next.js
   │
   └── Backend (Port 8000) - FastAPI
        ↓
        ├── PostgreSQL (Port 5432)
        ├── Redis (Port 6379)
        └── Celery Worker
```

All services run in Docker containers on a private network.
