#!/bin/bash

# 🚀 AstraTrade Deployment Script
# Automated deployment for local testing and production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FLUTTER_VERSION="3.32.5"

# Default values
ENVIRONMENT="development"
PLATFORM="all"
CLEAN_BUILD=false
RUN_TESTS=true
SKIP_ANALYSIS=false
VERBOSE=false

# Help function
show_help() {
    echo "🚀 AstraTrade Deployment Script"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment    Target environment (development|testnet|production)"
    echo "  -p, --platform       Target platform (android|ios|web|all)"
    echo "  -c, --clean          Clean build directories before building"
    echo "  -t, --skip-tests     Skip running tests"
    echo "  -a, --skip-analysis  Skip code analysis"
    echo "  -v, --verbose        Enable verbose output"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e testnet -p android"
    echo "  $0 --environment production --platform web --clean"
    echo "  $0 -e development -p all -v"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -p|--platform)
                PLATFORM="$2"
                shift 2
                ;;
            -c|--clean)
                CLEAN_BUILD=true
                shift
                ;;
            -t|--skip-tests)
                RUN_TESTS=false
                shift
                ;;
            -a|--skip-analysis)
                SKIP_ANALYSIS=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check if Flutter is installed
    if ! command -v flutter &> /dev/null; then
        log_error "Flutter is not installed. Please install Flutter first."
        exit 1
    fi
    
    # Check Flutter version
    CURRENT_VERSION=$(flutter --version | grep -o "Flutter [0-9.]*" | grep -o "[0-9.]*")
    log_info "Flutter version: $CURRENT_VERSION"
    
    # Check if we're in the correct directory
    if [[ ! -f "$PROJECT_ROOT/pubspec.yaml" ]]; then
        log_error "Not in a Flutter project directory"
        exit 1
    fi
    
    # Check if Web3Auth client ID is configured
    if [[ -z "${WEB3AUTH_CLIENT_ID:-}" ]] && [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        log_warning "Web3Auth client ID not configured. Using default demo mode."
    fi
    
    log_success "Prerequisites check completed"
}

# Configure environment
configure_environment() {
    log_step "Configuring environment: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        development)
            export STARKNET_NETWORK="sepolia-alpha"
            export API_BASE_URL="http://localhost:8000"
            export DEMO_MODE="false"
            ;;
        testnet)
            export STARKNET_NETWORK="sepolia-alpha"
            export API_BASE_URL="https://api-testnet.astratrade.io"
            export DEMO_MODE="false"
            ;;
        production)
            export STARKNET_NETWORK="starknet-mainnet"
            export API_BASE_URL="https://api.astratrade.io"
            export DEMO_MODE="false"
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    # Create .env file
    cat > "$PROJECT_ROOT/.env" << EOF
STARKNET_NETWORK=$STARKNET_NETWORK
API_BASE_URL=$API_BASE_URL
DEMO_MODE=$DEMO_MODE
WEB3AUTH_CLIENT_ID=${WEB3AUTH_CLIENT_ID:-BPPbhL4egAYdv3vHFVQDhmueoOJKUeHJZe2X8LaMvMIq9go2GN72j6OwvheQkR2ofq8WveHJQtzNKaq0_o_xKuI}
EOF
    
    log_success "Environment configured: $ENVIRONMENT"
}

# Clean build directories
clean_build() {
    if [[ "$CLEAN_BUILD" == true ]]; then
        log_step "Cleaning build directories..."
        cd "$PROJECT_ROOT"
        flutter clean
        rm -rf build/
        log_success "Build directories cleaned"
    fi
}

# Get dependencies
get_dependencies() {
    log_step "Getting Flutter dependencies..."
    cd "$PROJECT_ROOT"
    
    if [[ "$VERBOSE" == true ]]; then
        flutter pub get
    else
        flutter pub get > /dev/null 2>&1
    fi
    
    log_success "Dependencies downloaded"
}

# Run code analysis
run_analysis() {
    if [[ "$SKIP_ANALYSIS" == false ]]; then
        log_step "Running code analysis..."
        cd "$PROJECT_ROOT"
        
        if flutter analyze --fatal-infos --fatal-warnings; then
            log_success "Code analysis passed"
        else
            log_error "Code analysis failed"
            exit 1
        fi
    fi
}

# Run tests
run_tests() {
    if [[ "$RUN_TESTS" == true ]]; then
        log_step "Running tests..."
        cd "$PROJECT_ROOT"
        
        if flutter test; then
            log_success "Tests passed"
        else
            log_error "Tests failed"
            exit 1
        fi
    fi
}

# Build for Android
build_android() {
    log_step "Building Android APK..."
    cd "$PROJECT_ROOT"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        flutter build apk --release ${VERBOSE:+--verbose}
        flutter build appbundle --release ${VERBOSE:+--verbose}
        log_success "Android release build completed"
        log_info "APK: build/app/outputs/flutter-apk/app-release.apk"
        log_info "AAB: build/app/outputs/bundle/release/app-release.aab"
    else
        flutter build apk --debug ${VERBOSE:+--verbose}
        log_success "Android debug build completed"
        log_info "APK: build/app/outputs/flutter-apk/app-debug.apk"
    fi
}

# Build for iOS
build_ios() {
    log_step "Building iOS app..."
    cd "$PROJECT_ROOT"
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_warning "iOS build skipped (not on macOS)"
        return
    fi
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        flutter build ios --release --no-codesign ${VERBOSE:+--verbose}
        log_success "iOS release build completed"
    else
        flutter build ios --debug --simulator ${VERBOSE:+--verbose}
        log_success "iOS debug build completed"
    fi
    
    log_info "iOS build: build/ios/iphonesimulator/Runner.app"
}

# Build for Web
build_web() {
    log_step "Building web app..."
    cd "$PROJECT_ROOT"
    
    flutter build web --release ${VERBOSE:+--verbose}
    log_success "Web build completed"
    log_info "Web app: build/web/"
}

# Deploy based on platform
deploy() {
    log_step "Starting deployment for platform: $PLATFORM"
    
    case $PLATFORM in
        android)
            build_android
            ;;
        ios)
            build_ios
            ;;
        web)
            build_web
            ;;
        all)
            build_android
            build_ios
            build_web
            ;;
        *)
            log_error "Unknown platform: $PLATFORM"
            exit 1
            ;;
    esac
}

# Post-deployment tasks
post_deployment() {
    log_step "Running post-deployment tasks..."
    
    # Generate deployment report
    cat > "$PROJECT_ROOT/deployment_report.md" << EOF
# 🚀 AstraTrade Deployment Report

**Deployment Date:** $(date)
**Environment:** $ENVIRONMENT
**Platform:** $PLATFORM
**Flutter Version:** $(flutter --version | head -n 1)

## Build Status
- ✅ Dependencies: Downloaded
- ✅ Analysis: $([ "$SKIP_ANALYSIS" == false ] && echo "Passed" || echo "Skipped")
- ✅ Tests: $([ "$RUN_TESTS" == true ] && echo "Passed" || echo "Skipped")
- ✅ Build: Completed

## Configuration
- **Starknet Network:** $STARKNET_NETWORK
- **API Base URL:** $API_BASE_URL
- **Demo Mode:** $DEMO_MODE

## Build Artifacts
EOF
    
    if [[ "$PLATFORM" == "android" || "$PLATFORM" == "all" ]]; then
        echo "- **Android APK:** build/app/outputs/flutter-apk/" >> "$PROJECT_ROOT/deployment_report.md"
        if [[ "$ENVIRONMENT" == "production" ]]; then
            echo "- **Android AAB:** build/app/outputs/bundle/release/" >> "$PROJECT_ROOT/deployment_report.md"
        fi
    fi
    
    if [[ "$PLATFORM" == "ios" || "$PLATFORM" == "all" ]] && [[ "$OSTYPE" == "darwin"* ]]; then
        echo "- **iOS App:** build/ios/iphonesimulator/" >> "$PROJECT_ROOT/deployment_report.md"
    fi
    
    if [[ "$PLATFORM" == "web" || "$PLATFORM" == "all" ]]; then
        echo "- **Web App:** build/web/" >> "$PROJECT_ROOT/deployment_report.md"
    fi
    
    log_success "Deployment report generated: deployment_report.md"
}

# Main execution
main() {
    echo -e "${CYAN}"
    echo "🚀 AstraTrade Deployment Script"
    echo "=================================="
    echo -e "${NC}"
    
    parse_args "$@"
    check_prerequisites
    configure_environment
    clean_build
    get_dependencies
    run_analysis
    run_tests
    deploy
    post_deployment
    
    echo -e "${GREEN}"
    echo "🎉 Deployment completed successfully!"
    echo "📊 Summary:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Platform: $PLATFORM"
    echo "   Clean build: $CLEAN_BUILD"
    echo "   Tests run: $RUN_TESTS"
    echo "   Analysis: $([ "$SKIP_ANALYSIS" == false ] && echo "✅" || echo "⏭️")"
    echo -e "${NC}"
    
    if [[ "$PLATFORM" == "web" || "$PLATFORM" == "all" ]]; then
        echo -e "${BLUE}🌐 To serve the web app locally:${NC}"
        echo "   cd build/web && python3 -m http.server 8080"
        echo "   Open: http://localhost:8080"
    fi
}

# Run main function with all arguments
main "$@"