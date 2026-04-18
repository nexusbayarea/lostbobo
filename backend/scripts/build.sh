#!/bin/bash
# scripts/build.sh
# Local Build Authority (LBA) - Single Source of Truth for image creation

set -e

IMAGE_NAME="ghcr.io/nexusbayarea/simhpc-unified"
GIT_SHA=$(git rev-parse --short HEAD)

echo "🏗️ Building SimHPC Local Authority Image: $GIT_SHA"

# Validate build context
echo "🔍 Validating build context..."
if [ ! -f "./docker/images/Dockerfile.unified" ]; then
    echo "❌ Dockerfile.unified not found!"
    exit 1
fi

# Ensure we are in the root directory
cd "$(dirname "$0")/.." || exit

# Build locally with SHA tag
docker build -t $IMAGE_NAME:latest -t $IMAGE_NAME:$GIT_SHA -f ./docker/images/Dockerfile.unified .

# Push to Registry
echo "🚀 Pushing to GHCR..."
docker push $IMAGE_NAME:latest
docker push $IMAGE_NAME:$GIT_SHA

echo "✅ Local Build Complete: $IMAGE_NAME:$GIT_SHA"

