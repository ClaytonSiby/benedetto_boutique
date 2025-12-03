#!/bin/bash
# GCP Deployment Script
# This script builds and deploys the application to Cloud Run using Cloud Build

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}B Boutique - Cloud Run Deployment${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check prerequisites
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    exit 1
fi

# Get project info
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION=${REGION:-us-central1}

echo -e "Project ID: ${GREEN}${PROJECT_ID}${NC}"
echo -e "Region: ${GREEN}${REGION}${NC}\n"

# Confirm deployment
read -p "Deploy to Cloud Run? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 0
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Submit build to Cloud Build
echo -e "\n${GREEN}Submitting build to Cloud Build...${NC}"
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION="${REGION}" \
    --project="${PROJECT_ID}"

# Get service URLs
echo -e "\n${GREEN}Getting service URLs...${NC}"
BACKEND_URL=$(gcloud run services describe b-boutique-backend --region="${REGION}" --format='value(status.url)' --project="${PROJECT_ID}" 2>/dev/null || echo "Not deployed")
FRONTEND_URL=$(gcloud run services describe b-boutique-frontend --region="${REGION}" --format='value(status.url)' --project="${PROJECT_ID}" 2>/dev/null || echo "Not deployed")

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Backend URL:  ${GREEN}${BACKEND_URL}${NC}"
echo -e "Frontend URL: ${GREEN}${FRONTEND_URL}${NC}"
echo -e "\n${YELLOW}Note: Update GOOGLE_REDIRECT_URI and frontend NEXT_PUBLIC_API_URL with these URLs${NC}"
