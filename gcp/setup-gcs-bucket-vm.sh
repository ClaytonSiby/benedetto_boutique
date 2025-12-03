#!/bin/bash
# GCS Bucket Setup for VM (No Service Account Keys)
# This version attaches the service account to your VM instead of using keys

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GCS Bucket Setup for B Boutique (VM)${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project selected${NC}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "Project ID: ${GREEN}${PROJECT_ID}${NC}"

# Set variables
BUCKET_NAME="b-boutique-uploads-${PROJECT_ID}"
REGION="us-central1"
SERVICE_ACCOUNT_NAME="b-boutique-storage-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Prompt for region
read -p "Enter GCP region (default: ${REGION}): " input_region
if [ -n "$input_region" ]; then
    REGION=$input_region
fi

# Prompt for VM name
echo -e "\n${YELLOW}Enter your VM details:${NC}"
read -p "VM name: " VM_NAME
read -p "VM zone (e.g., us-central1-a): " VM_ZONE

if [ -z "$VM_NAME" ] || [ -z "$VM_ZONE" ]; then
    echo -e "${RED}Error: VM name and zone are required${NC}"
    exit 1
fi

echo -e "\n${YELLOW}This will:${NC}"
echo "  1. Create/verify GCS bucket: ${BUCKET_NAME}"
echo "  2. Create/verify service account: ${SERVICE_ACCOUNT_NAME}"
echo "  3. Grant storage permissions to service account"
echo "  4. Attach service account to VM: ${VM_NAME}"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Setup cancelled${NC}"
    exit 0
fi

# Enable required APIs
echo -e "\n${GREEN}Enabling required APIs...${NC}"
gcloud services enable storage-api.googleapis.com --project="${PROJECT_ID}" 2>/dev/null || true
gcloud services enable iam.googleapis.com --project="${PROJECT_ID}" 2>/dev/null || true
gcloud services enable compute.googleapis.com --project="${PROJECT_ID}" 2>/dev/null || true

# Create bucket
echo -e "\n${GREEN}Creating GCS bucket...${NC}"
if gsutil ls -b "gs://${BUCKET_NAME}" &>/dev/null; then
    echo -e "${YELLOW}Bucket already exists: ${BUCKET_NAME}${NC}"
else
    gsutil mb -p "${PROJECT_ID}" -l "${REGION}" -b on "gs://${BUCKET_NAME}"
    echo -e "${GREEN}✓ Bucket created: ${BUCKET_NAME}${NC}"
fi

# Set bucket to uniform access control
echo -e "\n${GREEN}Configuring bucket access...${NC}"
gsutil uniformbucketlevelaccess set on "gs://${BUCKET_NAME}" 2>/dev/null || true
echo -e "${GREEN}✓ Bucket access control configured${NC}"
echo -e "${YELLOW}Note: Objects will be made public individually when uploaded${NC}"

# Configure CORS
echo -e "\n${GREEN}Configuring CORS...${NC}"
cat > /tmp/cors.json <<EOF
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
EOF
gsutil cors set /tmp/cors.json "gs://${BUCKET_NAME}"
rm /tmp/cors.json
echo -e "${GREEN}✓ CORS configured${NC}"

# Create service account
echo -e "\n${GREEN}Creating service account...${NC}"
if gcloud iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Service account already exists${NC}"
else
    gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
        --display-name="B Boutique Storage Service Account" \
        --project="${PROJECT_ID}"
    echo -e "${GREEN}✓ Service account created${NC}"
fi

# Grant permissions to service account
echo -e "\n${GREEN}Granting storage permissions...${NC}"
gsutil iam ch "serviceAccount:${SERVICE_ACCOUNT_EMAIL}:roles/storage.objectAdmin" "gs://${BUCKET_NAME}"
echo -e "${GREEN}✓ Permissions granted${NC}"

# Stop the VM if running
echo -e "\n${GREEN}Preparing to attach service account to VM...${NC}"
VM_STATUS=$(gcloud compute instances describe "${VM_NAME}" --zone="${VM_ZONE}" --format="get(status)" 2>/dev/null || echo "NOT_FOUND")

if [ "$VM_STATUS" = "NOT_FOUND" ]; then
    echo -e "${RED}Error: VM '${VM_NAME}' not found in zone '${VM_ZONE}'${NC}"
    exit 1
fi

if [ "$VM_STATUS" = "RUNNING" ]; then
    echo -e "${YELLOW}VM is running. It needs to be stopped to attach the service account.${NC}"
    read -p "Stop VM now? (yes/no): " stop_confirm
    if [ "$stop_confirm" = "yes" ]; then
        echo -e "${YELLOW}Stopping VM...${NC}"
        gcloud compute instances stop "${VM_NAME}" --zone="${VM_ZONE}"
        echo -e "${GREEN}✓ VM stopped${NC}"
    else
        echo -e "${YELLOW}You'll need to stop the VM manually and run:${NC}"
        echo "gcloud compute instances set-service-account ${VM_NAME} \\"
        echo "  --zone=${VM_ZONE} \\"
        echo "  --service-account=${SERVICE_ACCOUNT_EMAIL} \\"
        echo "  --scopes=https://www.googleapis.com/auth/cloud-platform"
        exit 0
    fi
fi

# Attach service account to VM
echo -e "\n${GREEN}Attaching service account to VM...${NC}"
gcloud compute instances set-service-account "${VM_NAME}" \
    --zone="${VM_ZONE}" \
    --service-account="${SERVICE_ACCOUNT_EMAIL}" \
    --scopes=https://www.googleapis.com/auth/cloud-platform

echo -e "${GREEN}✓ Service account attached to VM${NC}"

# Start the VM
echo -e "\n${GREEN}Starting VM...${NC}"
gcloud compute instances start "${VM_NAME}" --zone="${VM_ZONE}"
echo -e "${GREEN}✓ VM started${NC}"

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Configuration Details:${NC}"
echo "Bucket Name: ${BUCKET_NAME}"
echo "Bucket URL: https://storage.googleapis.com/${BUCKET_NAME}"
echo "Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo "VM: ${VM_NAME} (zone: ${VM_ZONE})"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. SSH into your VM:"
echo "   gcloud compute ssh ${VM_NAME} --zone=${VM_ZONE}"
echo ""
echo "2. Update backend/.env.production with:"
echo "   GCP_PROJECT_ID=${PROJECT_ID}"
echo "   GCS_BUCKET_NAME=${BUCKET_NAME}"
echo "   USE_GCS=True"
echo "   # Remove or comment out: GOOGLE_APPLICATION_CREDENTIALS"
echo ""
echo "3. Update docker-compose.prod.yml:"
echo "   Remove the gcs-key.json volume mount (not needed)"
echo ""
echo "4. Restart your application:"
echo "   cd ~/b_boutique/backend"
echo "   docker-compose -f docker-compose.prod.yml restart backend celery_worker"
echo ""
echo -e "${GREEN}The VM will now use its service account for GCS access!${NC}"
echo -e "${YELLOW}No key files needed - this is more secure! 🔒${NC}"
