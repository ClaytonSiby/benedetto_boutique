# GCS Setup for VM - No Key Files Required! 🔒

## 🚨 Your Organization Blocks Service Account Keys

Your GCP organization has **`constraints/iam.disableServiceAccountKeyCreation`** enabled. This is a **security best practice**!

## ✅ Better Solution: Use VM Service Account

Instead of using key files, we'll attach the service account directly to your VM. The Python SDK will automatically use the VM's credentials.

## 🚀 Complete Setup

### Step 1: Run the VM Setup Script

```bash
cd backend/gcp
./setup-gcs-bucket-vm.sh
```

This will:
- ✅ Create/verify the GCS bucket
- ✅ Create/verify the service account  
- ✅ Grant storage permissions
- ✅ **Attach the service account to your VM**
- ✅ Restart your VM

You'll need to provide:
- Your VM name
- Your VM zone (e.g., `us-central1-a`)

### Step 2: Update .env.production on Your VM

SSH into your VM:
```bash
gcloud compute ssh YOUR_VM_NAME --zone=YOUR_ZONE
```

Edit the environment file:
```bash
cd ~/b_boutique/backend
nano .env.production
```

Add these lines:
```bash
# GCP Cloud Storage Settings
GCP_PROJECT_ID=benedetto-luxury-boutique
GCS_BUCKET_NAME=b-boutique-uploads-benedetto-luxury-boutique
USE_GCS=True

# DO NOT SET GOOGLE_APPLICATION_CREDENTIALS!
# The VM's service account will be used automatically
```

### Step 3: Ensure docker-compose.prod.yml is Updated

The file should NOT have:
- ❌ `gcs-key.json` volume mount
- ❌ `GOOGLE_APPLICATION_CREDENTIALS` environment variable

It should look like this:
```yaml
backend:
  # ...
  environment:
    - POSTGRES_SERVER=postgres
    - POSTGRES_PORT=5432
  volumes:
    - ./app:/app/app
    - ./alembic:/app/alembic
    - ./scripts:/app/scripts
    - uploads_data:/app/uploads
```

### Step 4: Restart Your Application

```bash
cd ~/b_boutique/backend
docker-compose -f docker-compose.prod.yml restart backend celery_worker
```

## 🔍 How It Works

1. **VM Service Account**: Your VM has a service account attached
2. **Metadata Service**: Docker containers can access the GCP metadata service at `http://metadata.google.internal`
3. **Application Default Credentials**: The Python `google-cloud-storage` library automatically:
   - Detects it's running on GCE
   - Fetches credentials from the metadata service
   - Uses them to authenticate to GCS

**No key files needed!** 🎉

## ✅ Verify It Works

### Check Backend Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

Look for:
- No authentication errors
- Successful GCS operations

### Test Upload
Try uploading an image through your API. The URL will be:
```
https://storage.googleapis.com/b-boutique-uploads-benedetto-luxury-boutique/uploads/filename.jpg
```

## 🔧 Troubleshooting

### Error: "Could not automatically determine credentials"

**Check VM Service Account:**
```bash
gcloud compute instances describe YOUR_VM_NAME \
  --zone=YOUR_ZONE \
  --format="get(serviceAccounts[0].email)"
```

Should show: `b-boutique-storage-sa@benedetto-luxury-boutique.iam.gserviceaccount.com`

**If not attached, run:**
```bash
# Stop VM
gcloud compute instances stop YOUR_VM_NAME --zone=YOUR_ZONE

# Attach service account
gcloud compute instances set-service-account YOUR_VM_NAME \
  --zone=YOUR_ZONE \
  --service-account=b-boutique-storage-sa@benedetto-luxury-boutique.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform

# Start VM
gcloud compute instances start YOUR_VM_NAME --zone=YOUR_ZONE
```

### Error: "403 Forbidden"

**Check service account has storage permissions:**
```bash
gsutil iam get gs://b-boutique-uploads-benedetto-luxury-boutique
```

Should include:
```
serviceAccount:b-boutique-storage-sa@benedetto-luxury-boutique.iam.gserviceaccount.com:roles/storage.objectAdmin
```

**If missing, grant permissions:**
```bash
gsutil iam ch serviceAccount:b-boutique-storage-sa@benedetto-luxury-boutique.iam.gserviceaccount.com:roles/storage.objectAdmin \
  gs://b-boutique-uploads-benedetto-luxury-boutique
```

## 🔒 Security Benefits

Using VM service accounts instead of key files:
- ✅ **No key management** - Keys can't be leaked
- ✅ **No key rotation** - VM credentials refresh automatically
- ✅ **Audit trail** - All access logged to the service account
- ✅ **Principle of least privilege** - Service account only has storage access
- ✅ **Organization policy compliant** - No key creation required

## 📊 Current Status

Based on your setup:
- ✅ Bucket created: `b-boutique-uploads-benedetto-luxury-boutique`
- ✅ Service account created: `b-boutique-storage-sa`
- ✅ Storage permissions granted
- ⏳ Need to complete: Attach service account to VM

## 🎯 Summary

**Old approach (blocked):**
```
VM → Key File → GCS
```

**New approach (secure):**
```
VM (with Service Account) → Metadata Service → GCS
```

**Result:** More secure, zero maintenance, no key files to manage! 🔐
