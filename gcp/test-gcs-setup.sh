#!/bin/bash
# Test GCS bucket setup
# Run this after setup-gcs-bucket.sh to verify everything works

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Testing GCS Setup...${NC}\n"

# Get bucket name from .env.production or prompt
if [ -f "../.env.production" ]; then
    BUCKET_NAME=$(grep GCS_BUCKET_NAME ../.env.production | cut -d '=' -f2)
fi

if [ -z "$BUCKET_NAME" ]; then
    read -p "Enter bucket name: " BUCKET_NAME
fi

echo -e "Bucket: ${GREEN}${BUCKET_NAME}${NC}\n"

# Test 1: Check if bucket exists
echo -e "${YELLOW}Test 1: Checking if bucket exists...${NC}"
if gsutil ls -b "gs://${BUCKET_NAME}" &>/dev/null; then
    echo -e "${GREEN}✓ Bucket exists${NC}\n"
else
    echo -e "${RED}✗ Bucket not found${NC}"
    exit 1
fi

# Test 2: Check CORS configuration
echo -e "${YELLOW}Test 2: Checking CORS configuration...${NC}"
CORS=$(gsutil cors get "gs://${BUCKET_NAME}")
if [ -n "$CORS" ]; then
    echo -e "${GREEN}✓ CORS configured${NC}\n"
else
    echo -e "${YELLOW}⚠ CORS not configured${NC}\n"
fi

# Test 3: Test upload
echo -e "${YELLOW}Test 3: Testing file upload...${NC}"
echo "test file" > /tmp/gcs-test.txt
if gsutil cp /tmp/gcs-test.txt "gs://${BUCKET_NAME}/test-upload.txt" &>/dev/null; then
    echo -e "${GREEN}✓ Upload successful${NC}"
    
    # Make it public and test access
    gsutil acl ch -u AllUsers:R "gs://${BUCKET_NAME}/test-upload.txt" &>/dev/null || true
    
    # Clean up
    gsutil rm "gs://${BUCKET_NAME}/test-upload.txt" &>/dev/null
    rm /tmp/gcs-test.txt
    echo -e "${GREEN}✓ Cleanup completed${NC}\n"
else
    echo -e "${RED}✗ Upload failed${NC}"
    rm /tmp/gcs-test.txt
    exit 1
fi

# Test 4: Check service account key
echo -e "${YELLOW}Test 4: Checking service account key...${NC}"
if [ -f "../gcs-key.json" ]; then
    echo -e "${GREEN}✓ Service account key found${NC}\n"
else
    echo -e "${RED}✗ Service account key not found at backend/gcs-key.json${NC}\n"
    exit 1
fi

# Test 5: Verify environment variables
echo -e "${YELLOW}Test 5: Checking environment configuration...${NC}"
REQUIRED_VARS=("GCP_PROJECT_ID" "GCS_BUCKET_NAME" "USE_GCS" "GOOGLE_APPLICATION_CREDENTIALS")
MISSING=()

if [ -f "../.env.production" ]; then
    for var in "${REQUIRED_VARS[@]}"; do
        if ! grep -q "^${var}=" ../.env.production 2>/dev/null; then
            MISSING+=("$var")
        fi
    done
    
    if [ ${#MISSING[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ All environment variables configured${NC}\n"
    else
        echo -e "${YELLOW}⚠ Missing variables in .env.production: ${MISSING[*]}${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ .env.production file not found${NC}\n"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GCS Setup Test Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo "1. Ensure all environment variables are set in .env.production"
echo "2. Copy gcs-key.json to your VM"
echo "3. Restart your backend service"
