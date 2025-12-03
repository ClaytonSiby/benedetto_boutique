#!/bin/bash
# Quick GCS setup for existing VM
# Uses the already created bucket and service account

set -e

PROJECT_ID="benedetto-luxury-boutique"
BUCKET_NAME="b-boutique-uploads-${PROJECT_ID}"
SERVICE_ACCOUNT_EMAIL="b-boutique-storage-sa@${PROJECT_ID}.iam.gserviceaccount.com"
VM_NAME="b-boutique"
VM_ZONE="us-central1-a"

echo "========================================="
echo "Attaching Service Account to VM"
echo "========================================="
echo ""
echo "VM: ${VM_NAME}"
echo "Zone: ${VM_ZONE}"
echo "Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

# Check VM status
VM_STATUS=$(gcloud compute instances describe "${VM_NAME}" --zone="${VM_ZONE}" --format="get(status)")
echo "Current VM status: ${VM_STATUS}"

if [ "$VM_STATUS" = "RUNNING" ]; then
    echo ""
    echo "⚠️  VM needs to be stopped to attach service account"
    read -p "Stop VM now? (yes/no): " stop_confirm
    
    if [ "$stop_confirm" = "yes" ]; then
        echo "Stopping VM..."
        gcloud compute instances stop "${VM_NAME}" --zone="${VM_ZONE}"
        echo "✓ VM stopped"
    else
        echo ""
        echo "Manual steps:"
        echo "1. Stop VM: gcloud compute instances stop ${VM_NAME} --zone=${VM_ZONE}"
        echo "2. Attach SA: gcloud compute instances set-service-account ${VM_NAME} --zone=${VM_ZONE} --service-account=${SERVICE_ACCOUNT_EMAIL} --scopes=https://www.googleapis.com/auth/cloud-platform"
        echo "3. Start VM: gcloud compute instances start ${VM_NAME} --zone=${VM_ZONE}"
        exit 0
    fi
fi

# Attach service account
echo ""
echo "Attaching service account..."
gcloud compute instances set-service-account "${VM_NAME}" \
    --zone="${VM_ZONE}" \
    --service-account="${SERVICE_ACCOUNT_EMAIL}" \
    --scopes=https://www.googleapis.com/auth/cloud-platform

echo "✓ Service account attached"

# Start VM
echo ""
echo "Starting VM..."
gcloud compute instances start "${VM_NAME}" --zone="${VM_ZONE}"
echo "✓ VM started"

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. SSH into VM:"
echo "   gcloud compute ssh ${VM_NAME} --zone=${VM_ZONE}"
echo ""
echo "2. Update ~/b_boutique/backend/.env.production:"
echo "   GCP_PROJECT_ID=${PROJECT_ID}"
echo "   GCS_BUCKET_NAME=${BUCKET_NAME}"
echo "   USE_GCS=True"
echo ""
echo "3. Restart backend:"
echo "   cd ~/b_boutique/backend"
echo "   docker-compose -f docker-compose.prod.yml restart backend celery_worker"
