#!/bin/bash
set -e

# Configuration
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
NAMESPACE="astratrade-${ENVIRONMENT}"

echo "🚀 Deploying AstraTrade ${VERSION} to ${ENVIRONMENT}"

# Build and push Docker images
echo "📦 Building Docker images..."
docker build -t astratrade/backend:${VERSION} ./backend
docker build -t astratrade/frontend:${VERSION} ./frontend

echo "📤 Pushing images to registry..."
docker push astratrade/backend:${VERSION}
docker push astratrade/frontend:${VERSION}

# Run database migrations
echo "🗄️ Running database migrations..."
kubectl run --rm -it migrate --image=astratrade/backend:${VERSION} \
  --restart=Never -- alembic upgrade head

# Deploy to Kubernetes
echo "☸️ Deploying to Kubernetes..."
kubectl apply -f k8s/${ENVIRONMENT}/ -n ${NAMESPACE}

# Update image versions
kubectl set image deployment/backend backend=astratrade/backend:${VERSION} -n ${NAMESPACE}
kubectl set image deployment/frontend frontend=astratrade/frontend:${VERSION} -n ${NAMESPACE}

# Wait for rollout
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/backend -n ${NAMESPACE}
kubectl rollout status deployment/frontend -n ${NAMESPACE}

# Run smoke tests
echo "🧪 Running smoke tests..."
python scripts/smoke_tests.py --environment ${ENVIRONMENT}

echo "✅ Deployment complete!"

