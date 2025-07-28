#!/bin/bash

# AstraTrade Context Management Script
# Integrates Claude Code Context Plugin with our project workflow

set -e

# Configuration
PLUGIN_ENGINE="/Users/admin/.claude/commands/orchestrator_engine.py"
PROJECT_ROOT="/Users/admin/AstraTrade-Project"
RAG_BACKEND="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[AstraTrade Context]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if plugin is installed
check_plugin() {
    if ! command -v claude-code-plugin &> /dev/null; then
        print_error "Claude Code Context Plugin not found"
        print_status "Installing plugin..."
        cd "$PROJECT_ROOT/claude-context-plugin"
        pip install -e .
        print_success "Plugin installed successfully"
    else
        print_success "Claude Code Context Plugin is available"
    fi
}

# Check orchestrator engine
check_orchestrator() {
    if [ ! -f "$PLUGIN_ENGINE" ]; then
        print_error "Orchestrator engine not found at $PLUGIN_ENGINE"
        exit 1
    fi
    print_success "Orchestrator engine is available"
}

# Check RAG backend status
check_rag() {
    if curl -s "$RAG_BACKEND/status" > /dev/null 2>&1; then
        print_success "RAG backend is running at $RAG_BACKEND"
        return 0
    else
        print_warning "RAG backend not accessible at $RAG_BACKEND"
        return 1
    fi
}

# Start context monitoring
start_monitoring() {
    print_status "Starting context monitoring for AstraTrade project..."
    
    # Check all dependencies
    check_plugin
    check_orchestrator
    check_rag
    
    # Initialize orchestrator with AstraTrade context
    python "$PLUGIN_ENGINE" --orchestrate --intent "Starting AstraTrade development session"
    
    print_success "Context monitoring started successfully"
}

# Get current status
get_status() {
    print_status "Getting current context status..."
    
    if [ -f "$PLUGIN_ENGINE" ]; then
        python "$PLUGIN_ENGINE" --status
    else
        print_error "Orchestrator engine not found"
        exit 1
    fi
}

# Analyze current context
analyze_context() {
    print_status "Analyzing current development context..."
    
    if [ -f "$PLUGIN_ENGINE" ]; then
        python "$PLUGIN_ENGINE" --analyze
    else
        print_error "Orchestrator engine not found"
        exit 1
    fi
}

# Orchestrate with specific intent
orchestrate() {
    local intent="$1"
    if [ -z "$intent" ]; then
        intent="General development task"
    fi
    
    print_status "Running orchestration with intent: $intent"
    
    if [ -f "$PLUGIN_ENGINE" ]; then
        python "$PLUGIN_ENGINE" --orchestrate --intent "$intent"
    else
        print_error "Orchestrator engine not found"
        exit 1
    fi
}

# Set development profile
set_profile() {
    local profile="$1"
    if [ -z "$profile" ]; then
        profile="dev"
    fi
    
    print_status "Setting development profile: $profile"
    
    if [ -f "$PLUGIN_ENGINE" ]; then
        python "$PLUGIN_ENGINE" --profile "$profile"
    else
        print_error "Orchestrator engine not found"
        exit 1
    fi
}

# Main command handler
case "$1" in
    "start"|"monitor")
        start_monitoring
        ;;
    "status")
        get_status
        ;;
    "analyze")
        analyze_context
        ;;
    "orchestrate")
        orchestrate "$2"
        ;;
    "profile")
        set_profile "$2"
        ;;
    "check")
        print_status "Checking all components..."
        check_plugin
        check_orchestrator
        check_rag
        print_success "All checks completed"
        ;;
    "help"|*)
        echo "AstraTrade Context Manager"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start, monitor    Start context monitoring"
        echo "  status           Show current context status"
        echo "  analyze          Analyze current development context"
        echo "  orchestrate [intent]  Run orchestration with specific intent"
        echo "  profile [name]   Set development profile (dev, research, debug, doc)"
        echo "  check            Check all component availability"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 orchestrate 'Implementing trading feature'"
        echo "  $0 profile dev"
        echo "  $0 status"
        ;;
esac