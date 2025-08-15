# Implementation Plan: Enhanced Infrastructure Deployment

Generated on: Sat Aug  2 19:55:19 +07 2025

## Deployment Strategy Overview

### Objective
Successfully deploy the enhanced AstraTrade infrastructure with all advanced features operational, resolving current dependency and deployment blockers.

### Current Status
- ✅ **Enhanced Infrastructure Code**: All features implemented and tested conceptually
- ❌ **Deployment Blocked**: Python dependency compilation failures
- ❌ **Services Not Running**: Real microservices not operational
- ❌ **Integration Untested**: Enhanced features not validated in live environment

## Phase 1: Dependency Resolution (Priority: Critical)

### Problem Analysis
Current pip installation fails due to:
- **asyncpg**: PostgreSQL adapter requires system libraries
- **orjson**: Fast JSON library requires Rust compiler  
- **pydantic-core**: Core validation library compilation issues

### Solution: Docker-First Approach (Recommended)
Use containerized deployment to avoid local dependency compilation issues.

### Implementation Steps

#### Step 1.1: Create Production Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Expose port
EXPOSE 8000

# Start API Gateway
CMD ["python", "api_gateway.py"]
```

#### Step 1.2: Build and Test Base Image
```bash
# Build enhanced infrastructure image
docker build -t astratrade-enhanced .

# Test import of critical modules
docker run --rm astratrade-enhanced python -c "
from infrastructure.monitoring.business_metrics import business_metrics
from slowapi import Limiter
print('✅ All dependencies working')
"
```

## Phase 2: Infrastructure Deployment

### Step 2.1: Redis Infrastructure
```bash
# Start Redis for service discovery and rate limiting
docker run -d --name redis \
  -p 6379:6379 \
  --restart unless-stopped \
  redis:alpine redis-server --appendonly yes
  
# Verify Redis connectivity
docker exec redis redis-cli ping
```

### Step 2.2: Enhanced API Gateway
```bash
# Deploy API Gateway with enhanced features
docker run -d --name api-gateway \
  -p 8000:8000 \
  --link redis:redis \
  -e REDIS_URL=redis://redis:6379 \
  astratrade-enhanced

# Wait for startup and test
sleep 10
curl http://localhost:8000/health
```

### Step 2.3: Microservices Deployment
```bash
# Deploy in dependency order
# User Service (Port 8004)
docker run -d --name user-service \
  -p 8004:8004 \
  --link redis:redis \
  astratrade-enhanced python services/user/main.py

# Trading Service (Port 8001) 
docker run -d --name trading-service \
  -p 8001:8001 \
  --link redis:redis \
  astratrade-enhanced python services/trading/main.py

# Additional services follow same pattern...
```

## Phase 3: Feature Validation

### Step 3.1: Service Discovery Validation
```bash
# Check service registration
curl http://localhost:8000/services

# Expected output: All services registered and healthy
```

### Step 3.2: Circuit Breaker Testing
```bash
# Test circuit breaker under failure
# Stop a service to trigger circuit opening
docker stop trading-service

# Verify circuit breaker protection
curl http://localhost:8000/api/v1/trading/execute
# Should return fallback response

# Restart service and verify recovery
docker start trading-service
sleep 30
curl http://localhost:8000/api/v1/trading/execute
# Should return normal response
```

### Step 3.3: Rate Limiting Validation
```bash
# Test per-user rate limiting (200 req/min)
for i in {1..210}; do
  curl -H "X-User-ID: test-user" \
       -w "%{http_code}\n" \
       http://localhost:8000/health > /dev/null
done
# Requests 201-210 should return 429
```

### Step 3.4: Business Metrics Validation
```bash
# Execute test trade
curl -X POST http://localhost:8000/api/v1/trading/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "asset_symbol": "BTC/USD", 
    "direction": "LONG",
    "amount": 1000
  }'

# Check business dashboard
curl http://localhost:8000/dashboard
# Should show updated KPIs
```

## Phase 4: Production Readiness

### Step 4.1: Performance Validation
```bash
# Load testing with Apache Bench
ab -n 1000 -c 50 http://localhost:8000/health

# Verify response times <100ms for 95th percentile
```

### Step 4.2: Monitoring Stack (Optional)
```bash
# Deploy Prometheus
docker run -d --name prometheus \
  -p 9090:9090 \
  prom/prometheus

# Deploy Grafana  
docker run -d --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

## Success Criteria Checklist

### Must Have (Deployment Blocking)
- [ ] All Python dependencies install successfully in Docker
- [ ] API Gateway starts and responds on port 8000
- [ ] `/health` endpoint returns service status
- [ ] `/services` shows at least one registered service
- [ ] Basic API endpoint responds (e.g., `/api/v1/trading/execute`)
- [ ] Business metrics collecting data

### Should Have (Production Ready)
- [ ] Circuit breakers activate under service failures
- [ ] Rate limiting blocks excessive requests
- [ ] Distributed tracing shows correlation IDs
- [ ] All 6 microservices running and registered
- [ ] Performance <100ms response time

### Nice to Have (Advanced)
- [ ] Prometheus metrics exported
- [ ] Grafana dashboards operational
- [ ] Container resource usage within limits

## Risk Mitigation

### Critical Risks
1. **Docker Resource Exhaustion**
   - Monitor: `docker stats`
   - Limit: `--memory=512m --cpus=0.5`
   - Rollback: Stop containers gracefully

2. **Port Conflicts**
   - Check: `netstat -tulpn | grep :8000`
   - Resolution: Kill conflicting processes
   - Alternative: Use different ports

3. **Redis Connection Failures**
   - Validate: `docker exec redis redis-cli ping`
   - Recovery: Restart Redis container
   - Fallback: Use in-memory service registry

## Rollback Plan
1. **Emergency Stop**: `docker stop api-gateway $(docker ps -q --filter name=*-service)`
2. **Clean State**: `docker rm api-gateway $(docker ps -aq --filter name=*-service)`
3. **Preserve Data**: `docker volume ls` (backup if needed)
4. **Restart Previous**: Use previous working configuration

## Timeline Estimate
- **Phase 1**: 30-60 minutes (dependency resolution)
- **Phase 2**: 30-60 minutes (infrastructure deployment)  
- **Phase 3**: 30-60 minutes (feature validation)
- **Phase 4**: 30 minutes (production readiness)
- **Total**: 2-4 hours for complete deployment

This plan provides a systematic approach to successfully deploy the enhanced infrastructure with proper validation and rollback capabilities.

