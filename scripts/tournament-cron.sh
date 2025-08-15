#!/bin/bash

# Tournament AI Trading Cron Job Script
# Runs AI trading cycles every 30 seconds
# Production deployment script

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/ai-trading.pid"
LOG_FILE="$LOG_DIR/ai-trading-cron.log"

# Environment Configuration
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-astratrade_redis_2024}"
AI_CYCLE_INTERVAL="${AI_CYCLE_INTERVAL:-30}"
MAX_CYCLES="${MAX_CYCLES:-2880}" # 24 hours worth of 30-second cycles

# Docker Configuration
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.tournament.yml"
COMPETITION_SERVICE_CONTAINER="astratrade-competition-service"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "ERROR: $1"
    cleanup
    exit 1
}

# Cleanup function
cleanup() {
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
    fi
}

# Check if another instance is running
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log "AI trading scheduler already running with PID $pid"
            exit 0
        else
            log "Stale PID file found, removing"
            rm -f "$PID_FILE"
        fi
    fi
}

# Health check for dependencies
health_check() {
    log "Performing health checks..."
    
    # Check Redis connectivity
    if ! docker exec "$COMPETITION_SERVICE_CONTAINER" redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" ping >/dev/null 2>&1; then
        handle_error "Redis health check failed"
    fi
    
    # Check competition service
    if ! docker exec "$COMPETITION_SERVICE_CONTAINER" curl -f http://localhost:8001/health >/dev/null 2>&1; then
        handle_error "Competition service health check failed"
    fi
    
    log "Health checks passed"
}

# Execute AI trading cycle
execute_ai_cycle() {
    local cycle_count=$1
    log "Executing AI trading cycle $cycle_count"
    
    # Call the competition service AI trading endpoint
    local response
    if response=$(docker exec "$COMPETITION_SERVICE_CONTAINER" curl -s -f -X POST http://localhost:8001/api/internal/ai-trading-cycle); then
        local trades_generated
        trades_generated=$(echo "$response" | jq -r '.trades_generated // 0' 2>/dev/null || echo "0")
        log "AI trading cycle $cycle_count completed: $trades_generated trades generated"
        return 0
    else
        log "ERROR: AI trading cycle $cycle_count failed"
        return 1
    fi
}

# Monitor system resources
monitor_resources() {
    local memory_usage
    local cpu_usage
    
    memory_usage=$(docker stats --no-stream --format "table {{.MemUsage}}" "$COMPETITION_SERVICE_CONTAINER" | tail -n +2)
    cpu_usage=$(docker stats --no-stream --format "table {{.CPUPerc}}" "$COMPETITION_SERVICE_CONTAINER" | tail -n +2)
    
    log "System resources - Memory: $memory_usage, CPU: $cpu_usage"
    
    # Alert if resource usage is too high
    local mem_percent
    mem_percent=$(echo "$memory_usage" | grep -o '[0-9.]*%' | head -1 | tr -d '%' || echo "0")
    local cpu_percent
    cpu_percent=$(echo "$cpu_usage" | tr -d '%' || echo "0")
    
    if (( $(echo "$mem_percent > 90" | bc -l) )); then
        log "WARNING: High memory usage detected: ${mem_percent}%"
    fi
    
    if (( $(echo "$cpu_percent > 90" | bc -l) )); then
        log "WARNING: High CPU usage detected: ${cpu_percent}%"
    fi
}

# Main AI trading loop
main() {
    log "Starting AI trading scheduler (PID: $$)"
    echo $$ > "$PID_FILE"
    
    # Trap signals for graceful shutdown
    trap cleanup EXIT
    trap 'log "Received SIGTERM, shutting down gracefully"; exit 0' TERM
    trap 'log "Received SIGINT, shutting down gracefully"; exit 0' INT
    
    # Initial health check
    health_check
    
    local cycle_count=0
    local consecutive_failures=0
    local start_time
    start_time=$(date +%s)
    
    log "AI trading scheduler started, running for up to $MAX_CYCLES cycles"
    
    while [[ $cycle_count -lt $MAX_CYCLES ]]; do
        cycle_count=$((cycle_count + 1))
        
        # Execute AI trading cycle
        if execute_ai_cycle "$cycle_count"; then
            consecutive_failures=0
        else
            consecutive_failures=$((consecutive_failures + 1))
            
            # Handle consecutive failures
            if [[ $consecutive_failures -ge 5 ]]; then
                handle_error "Too many consecutive AI trading cycle failures ($consecutive_failures)"
            fi
        fi
        
        # Monitor resources every 10 cycles (5 minutes)
        if [[ $((cycle_count % 10)) -eq 0 ]]; then
            monitor_resources
            
            # Log progress
            local elapsed_time
            elapsed_time=$(($(date +%s) - start_time))
            local cycles_per_hour
            cycles_per_hour=$(echo "scale=2; $cycle_count * 3600 / $elapsed_time" | bc -l)
            log "Progress: $cycle_count/$MAX_CYCLES cycles completed, rate: $cycles_per_hour cycles/hour"
        fi
        
        # Health check every hour (120 cycles)
        if [[ $((cycle_count % 120)) -eq 0 ]]; then
            health_check
        fi
        
        # Sleep for the specified interval
        sleep "$AI_CYCLE_INTERVAL"
    done
    
    log "AI trading scheduler completed $cycle_count cycles"
    cleanup
}

# Initialize logging
mkdir -p "$LOG_DIR"

# Handle command line arguments
case "${1:-start}" in
    start)
        check_running
        main
        ;;
    stop)
        if [[ -f "$PID_FILE" ]]; then
            local pid
            pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                log "Stopping AI trading scheduler (PID: $pid)"
                kill -TERM "$pid"
                # Wait for graceful shutdown
                for i in {1..30}; do
                    if ! kill -0 "$pid" 2>/dev/null; then
                        break
                    fi
                    sleep 1
                done
                # Force kill if still running
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid"
                fi
                rm -f "$PID_FILE"
                log "AI trading scheduler stopped"
            else
                log "AI trading scheduler not running"
            fi
        else
            log "AI trading scheduler not running (no PID file)"
        fi
        ;;
    status)
        if [[ -f "$PID_FILE" ]]; then
            local pid
            pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                log "AI trading scheduler is running (PID: $pid)"
            else
                log "AI trading scheduler not running (stale PID file)"
            fi
        else
            log "AI trading scheduler not running"
        fi
        ;;
    restart)
        "$0" stop
        sleep 2
        "$0" start
        ;;
    health)
        health_check
        log "Health check completed successfully"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|health}"
        exit 1
        ;;
esac