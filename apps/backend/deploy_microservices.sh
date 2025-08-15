#!/bin/bash

# AstraTrade Microservices Deployment Script
# Implements gradual migration strategy from plan.md

set -e

echo "🚀 AstraTrade Microservices Deployment"
echo "======================================"

# Configuration
COMPOSE_FILE="docker-compose.microservices.yml"
TIMEOUT=120
HEALTH_CHECK_INTERVAL=5

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    
    # Check compose file
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Compose file $COMPOSE_FILE not found."
        exit 1
    fi
    
    log_info "Prerequisites check passed ✅"
}

wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=$((TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=0
    
    log_info "Waiting for $service_name to be healthy..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
            log_info "$service_name is healthy ✅"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    log_error "$service_name health check failed after $TIMEOUT seconds"
    return 1
}

deploy_infrastructure() {
    log_info "Deploying infrastructure services..."
    
    # Start PostgreSQL and Redis
    docker-compose -f $COMPOSE_FILE up -d postgres redis
    
    # Wait for infrastructure
    log_info "Waiting for PostgreSQL..."
    while ! docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U astrauser -d astradb; do
        echo -n "."
        sleep 2
    done
    echo ""
    log_info "PostgreSQL is ready ✅"
    
    log_info "Waiting for Redis..."
    while ! docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping > /dev/null; do
        echo -n "."
        sleep 2
    done
    echo ""
    log_info "Redis is ready ✅"
    
    # Setup Redis Streams consumer groups
    if [ -f "setup_redis_streams.sh" ]; then
        log_info "Setting up Redis Streams consumer groups..."
        ./setup_redis_streams.sh
    fi
}

deploy_services_gradual() {
    log_info "Deploying services in gradual migration order..."
    
    # Phase 1: User Service (foundational, minimal dependencies)
    log_info "Phase 1: Deploying User Service..."
    docker-compose -f $COMPOSE_FILE up -d user-service
    wait_for_service "user-service" 8006 || exit 1
    
    # Phase 2: NFT Service (low complexity, low traffic)
    log_info "Phase 2: Deploying NFT Service..."
    docker-compose -f $COMPOSE_FILE up -d nft-service
    wait_for_service "nft-service" 8005 || exit 1
    
    # Phase 3: Financial Service (medium complexity)
    log_info "Phase 3: Deploying Financial Service..."
    docker-compose -f $COMPOSE_FILE up -d financial-service
    wait_for_service "financial-service" 8004 || exit 1
    
    # Phase 4: Social Service (multiple dependencies)
    log_info "Phase 4: Deploying Social Service..."
    docker-compose -f $COMPOSE_FILE up -d social-service
    wait_for_service "social-service" 8003 || exit 1
    
    # Phase 5: Gamification Service (complex event processing)
    log_info "Phase 5: Deploying Gamification Service..."
    docker-compose -f $COMPOSE_FILE up -d gamification-service
    wait_for_service "gamification-service" 8002 || exit 1
    
    # Phase 6: Trading Service (core business logic, critical)
    log_info "Phase 6: Deploying Trading Service..."
    docker-compose -f $COMPOSE_FILE up -d trading-service
    wait_for_service "trading-service" 8001 || exit 1
}

validate_deployment() {
    log_info "Validating microservices deployment..."
    
    # Check all services are running
    services=("user-service:8006" "trading-service:8001" "gamification-service:8002" 
              "social-service:8003" "financial-service:8004" "nft-service:8005")
    
    all_healthy=true
    
    for service_port in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        
        if ! curl -f -s "http://localhost:$port/health" > /dev/null; then
            log_error "$service health check failed"
            all_healthy=false
        else
            log_info "$service is healthy ✅"
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        log_info "All microservices are healthy ✅"
        return 0
    else
        log_error "Some services are unhealthy ❌"
        return 1
    fi
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    # Test API Gateway routing
    log_info "Testing API Gateway routing..."
    
    # Test user service through gateway (if API gateway is configured)
    if curl -f -s "http://localhost:8000/api/v1/users/health" > /dev/null 2>&1; then
        log_info "API Gateway routing to user service ✅"
    else
        log_warning "API Gateway routing test skipped (direct service access)"
    fi
    
    # Test service-to-service communication
    log_info "Testing service endpoints..."
    
    # Test User Service
    if curl -f -s "http://localhost:8006/api/v1/users/health" > /dev/null; then
        log_info "User service endpoint test ✅"
    else
        log_error "User service endpoint test failed ❌"
    fi
    
    # Test Trading Service
    if curl -f -s "http://localhost:8001/api/v1/trading/health" > /dev/null; then
        log_info "Trading service endpoint test ✅"
    else
        log_error "Trading service endpoint test failed ❌"
    fi
    
    log_info "Integration tests completed"
}

show_deployment_status() {
    log_info "Deployment Status Summary"
    echo "========================="
    
    # Show running containers
    echo "Running Containers:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    echo "Service Endpoints:"
    echo "- User Service:          http://localhost:8006"
    echo "- Trading Service:       http://localhost:8001" 
    echo "- Gamification Service:  http://localhost:8002"
    echo "- Social Service:        http://localhost:8003"
    echo "- Financial Service:     http://localhost:8004"
    echo "- NFT Service:           http://localhost:8005"
    echo ""
    echo "Infrastructure:"
    echo "- PostgreSQL:            localhost:5432"
    echo "- Redis:                 localhost:6379"
    echo ""
    echo "Monitoring (if enabled):"
    echo "- Prometheus:            http://localhost:9090"
    echo "- Grafana:               http://localhost:3000"
}

cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."
    docker-compose -f $COMPOSE_FILE down
    exit 1
}

# Main deployment flow
main() {
    # Handle interrupts
    trap cleanup_on_error INT TERM
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            deploy_infrastructure
            deploy_services_gradual
            validate_deployment
            run_integration_tests
            show_deployment_status
            log_info "Microservices deployment completed successfully! 🎉"
            ;;
        "stop")
            log_info "Stopping all microservices..."
            docker-compose -f $COMPOSE_FILE down
            log_info "All services stopped"
            ;;
        "status")
            show_deployment_status
            ;;
        "test")
            validate_deployment
            run_integration_tests
            ;;
        "monitoring")
            log_info "Starting monitoring stack..."
            docker-compose -f $COMPOSE_FILE --profile monitoring up -d
            log_info "Monitoring stack started"
            ;;
        *)
            echo "Usage: $0 {deploy|stop|status|test|monitoring}"
            echo ""
            echo "Commands:"
            echo "  deploy     - Deploy all microservices (default)"
            echo "  stop       - Stop all services"
            echo "  status     - Show deployment status"
            echo "  test       - Run validation and integration tests"
            echo "  monitoring - Start monitoring stack (Prometheus/Grafana)"
            exit 1
            ;;
    esac
}

main "$@"