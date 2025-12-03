#!/bin/bash
# Simple GCS Bucket Setup for B Boutique File Uploads
# This script creates a GCS bucket for your existing VM deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GCS Bucket Setup for B Boutique${NC}"
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

# Prompt for region
read -p "Enter GCP region (default: ${REGION}): " input_region
if [ -n "$input_region" ]; then
    REGION=$input_region
fi

echo -e "\n${YELLOW}This will create:${NC}"
echo "  - GCS bucket: ${BUCKET_NAME}"
echo "  - Service account: ${SERVICE_ACCOUNT_NAME}"
echo "  - Service account key (saved locally)"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Setup cancelled${NC}"
    exit 0
fi

# Enable required APIs
echo -e "\n${GREEN}Enabling required APIs...${NC}"
gcloud services enable storage-api.googleapis.com --project="${PROJECT_ID}"
gcloud services enable iam.googleapis.com --project="${PROJECT_ID}"

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
gsutil uniformbucketlevelaccess set on "gs://${BUCKET_NAME}"
echo -e "${GREEN}✓ Bucket access control configured${NC}"

# Note: We'll make objects public when uploaded, not the whole bucket
# This avoids organization policy restrictions
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
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

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

# Create and download service account key
KEY_FILE="../backend/gcs-key.json"
echo -e "\n${GREEN}Creating service account key...${NC}"
gcloud iam service-accounts keys create "${KEY_FILE}" \
    --iam-account="${SERVICE_ACCOUNT_EMAIL}" \
    --project="${PROJECT_ID}"
echo -e "${GREEN}✓ Key saved to: ${KEY_FILE}${NC}"

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Configuration Details:${NC}"
echo "Bucket Name: ${BUCKET_NAME}"
echo "Bucket URL: https://storage.googleapis.com/${BUCKET_NAME}"
echo "Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo "Key File: ${KEY_FILE}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update your .env.production file with:"
echo "   GCP_PROJECT_ID=${PROJECT_ID}"
echo "   GCS_BUCKET_NAME=${BUCKET_NAME}"
echo "   USE_GCS=True"
echo "   GOOGLE_APPLICATION_CREDENTIALS=/app/gcs-key.json"
echo ""
echo "2. Copy the key file to your VM:"
echo "   gcloud compute scp backend/gcs-key.json YOUR_VM_NAME:~/b_boutique/backend/ --zone=YOUR_ZONE"
echo ""
echo "3. Update docker-compose.prod.yml to mount the key file (see GCS_SETUP.md)"
echo ""
echo "4. Restart your application:"
echo "   docker-compose -f docker-compose.prod.yml restart backend"
echo ""
echo -e "${RED}IMPORTANT: Keep gcs-key.json secure and never commit it to git!${NC}"
