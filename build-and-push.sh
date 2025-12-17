#!/bin/bash
# Build and push Docker image to Azure Container Registry
# Usage: ./build-and-push.sh [tag]

set -e

# Configuration
ACR_NAME="zinfradevv1"
IMAGE_NAME="z-agent-metrics"
DEFAULT_TAG="latest"
TAG=${1:-$DEFAULT_TAG}
FULL_IMAGE_NAME="${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${TAG}"

echo "🚀 Building and pushing ${IMAGE_NAME} to Azure Container Registry..."
echo "================================================="

# Login to Azure Container Registry
echo "📝 Logging into Azure Container Registry: ${ACR_NAME}"
az acr login --name ${ACR_NAME}

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to Azure Container Registry"
    exit 1
fi

echo "✅ Successfully logged into Azure Container Registry"

# Build Docker image
echo "🔨 Building Docker image: ${FULL_IMAGE_NAME}"
docker build -t ${FULL_IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo "✅ Docker image built successfully"

# Push Docker image
echo "📤 Pushing Docker image to ACR: ${FULL_IMAGE_NAME}"
docker push ${FULL_IMAGE_NAME}

if [ $? -ne 0 ]; then
    echo "❌ Failed to push Docker image"
    exit 1
fi

echo "✅ Docker image pushed successfully"
echo "================================================="
echo "🎉 Build and push completed successfully!"
echo "📦 Image: ${FULL_IMAGE_NAME}"
echo ""
echo "🔧 To deploy to Kubernetes, run:"
echo "   kubectl apply -f z-agent-metrics-cronjob.yaml"