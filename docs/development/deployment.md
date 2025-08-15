# Deployment Guide

## Overview

This guide covers deployment procedures for all AstraTrade components including the Flutter frontend, FastAPI backend, and Cairo smart contracts.

## Deployment Environments

### Development
- **Frontend**: Local development server (`flutter run`)
- **Backend**: Local FastAPI server with hot reload
- **Contracts**: Local Starknet devnet
- **Database**: Local PostgreSQL instance

### Staging  
- **Frontend**: Web deployment with staging API
- **Backend**: Staging server with test data
- **Contracts**: Starknet Sepolia testnet
- **Database**: Staging database with anonymized data

### Production
- **Frontend**: Web and mobile app stores
- **Backend**: Production servers with load balancing
- **Contracts**: Starknet mainnet
- **Database**: Production database with backups

## Frontend Deployment

### Web Deployment

```bash
# Build for web
cd apps/frontend
flutter build web --release

# Deploy to hosting (example: Netlify)
netlify deploy --dir=build/web --prod
```

### Mobile App Deployment

#### iOS App Store

```bash
# Build iOS release
flutter build ios --release

# Archive and upload via Xcode or App Store Connect
open ios/Runner.xcworkspace
```

#### Google Play Store

```bash
# Build Android App Bundle
flutter build appbundle --release

# Upload to Google Play Console
# File: build/app/outputs/bundle/release/app-release.aab
```

### Environment Configuration

**Production Config**: `apps/frontend/lib/config/app_config.dart`

```dart
class AppConfig {
  static const String apiBaseUrl = 'https://api.astratrade.com';
  static const String environment = 'production';
  static const bool enableMockTrading = false;
}
```

## Backend Deployment

### Docker Deployment

#### 1. Build Docker Images

```bash
cd apps/backend
docker build -t astratrade-backend .

# Build microservices
docker-compose -f docker-compose.microservices.yml build
```

#### 2. Production Deployment

```bash
# Deploy with Docker Compose
docker-compose -f docker-compose.yml up -d

# Monitor services
docker-compose ps
docker-compose logs -f
```

### Manual Deployment

#### 1. Server Setup

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3.11 python3-pip postgresql redis-server

# Create application user
sudo useradd -m -s /bin/bash astratrade
```

#### 2. Application Deployment

```bash
# Clone and setup
git clone <repository>
cd AstraTrade-Project-Phase-2/apps/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
alembic upgrade head

# Start services with systemd
sudo systemctl enable astratrade-backend
sudo systemctl start astratrade-backend
```

### Load Balancing

**Nginx Configuration**: `/etc/nginx/sites-available/astratrade`

```nginx
upstream astratrade_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name api.astratrade.com;
    
    location / {
        proxy_pass http://astratrade_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Smart Contract Deployment

### Starknet Sepolia (Staging)

```bash
# Set environment variables
export STARKNET_ACCOUNT="./deployment_account.json"
export STARKNET_KEYSTORE="./deployment_account.json"

# Deploy contracts
python scripts/deployment/deploy_astratrade_v2.py

# Verify deployment
python scripts/testing/test_deployed_contracts.py
```

### Starknet Mainnet (Production)

```bash
# Use production account
export STARKNET_NETWORK="mainnet"
export STARKNET_ACCOUNT="./production_account.json"

# Deploy with additional verification
python scripts/deployment/secure_deploy.py

# Comprehensive testing
python scripts/testing/test_mainnet_deployment.py
```

### Contract Verification

```bash
# Verify on StarkScan
starkli verify <contract_address> <contract_class_hash>

# Automated verification
python scripts/deployment/verify_contracts.py
```

## Database Deployment

### PostgreSQL Setup

#### Production Database

```sql
-- Create database and user
CREATE DATABASE astratrade_prod;
CREATE USER astratrade WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE astratrade_prod TO astratrade;

-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

#### Backup Strategy

```bash
# Daily backups
0 2 * * * pg_dump astratrade_prod > /backups/astratrade_$(date +\%Y\%m\%d).sql

# Point-in-time recovery setup
archive_mode = on
archive_command = 'cp %p /backups/archive/%f'
```

### Redis Deployment

#### Production Configuration

```bash
# redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### Clustering (Optional)

```bash
# Redis Cluster setup
redis-server cluster-config/redis-6379.conf
redis-server cluster-config/redis-6380.conf
redis-server cluster-config/redis-6381.conf

redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381
```

## Monitoring and Alerting

### Application Monitoring

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'astratrade-backend'
    static_configs:
      - targets: ['localhost:8000']
```

#### Grafana Dashboards

- **Business KPIs**: User activity, trading volume, revenue metrics
- **System Metrics**: Response times, error rates, resource usage
- **Event Bus**: Message throughput, queue sizes, processing times

### Log Management

```bash
# Centralized logging with ELK stack
docker-compose -f docker-compose.monitoring.yml up -d

# Log aggregation
journalctl -u astratrade-backend -f | filebeat
```

## Security Deployment

### SSL/TLS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name api.astratrade.com;
    
    ssl_certificate /etc/letsencrypt/live/api.astratrade.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.astratrade.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### API Security

- Rate limiting configuration
- CORS policy setup
- API key management
- Request validation
- Security headers

### Database Security

- Connection encryption
- User privilege management
- Audit logging
- Backup encryption
- Network security groups

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates valid
- [ ] Monitoring configured
- [ ] Backup procedures tested

### Deployment Steps

- [ ] Backend services deployed
- [ ] Database migrations applied
- [ ] Smart contracts deployed
- [ ] Frontend builds completed
- [ ] Load balancer configured
- [ ] Monitoring alerts enabled

### Post-Deployment

- [ ] Health checks passing
- [ ] Performance metrics normal
- [ ] Error rates acceptable
- [ ] User acceptance testing
- [ ] Documentation updated
- [ ] Team notifications sent

## Rollback Procedures

### Application Rollback

```bash
# Rollback to previous version
docker-compose down
git checkout previous-release-tag
docker-compose up -d
```

### Database Rollback

```bash
# Rollback migrations
alembic downgrade <previous_revision>

# Restore from backup if needed
pg_restore -d astratrade_prod /backups/astratrade_backup.sql
```

### Smart Contract Rollback

Note: Smart contracts cannot be rolled back once deployed. Ensure thorough testing before mainnet deployment.

## Performance Optimization

### Backend Optimization

- Connection pooling configuration
- Cache warming strategies
- Database query optimization
- Redis memory optimization
- Load balancing tuning

### Frontend Optimization

- Bundle size optimization
- Image compression and lazy loading
- API request batching
- Local storage optimization
- Performance monitoring

## Troubleshooting

### Common Deployment Issues

**Issue**: Database connection failures
**Solution**: Check connection strings, firewall rules, and credentials

**Issue**: Redis connection timeouts
**Solution**: Verify Redis configuration and network connectivity

**Issue**: Smart contract deployment failures
**Solution**: Check account balance, network status, and contract syntax

**Issue**: Frontend build failures
**Solution**: Clear Flutter cache, update dependencies, check environment

### Emergency Procedures

- Service restart procedures
- Database failover process
- Emergency contact information
- Incident response playbook