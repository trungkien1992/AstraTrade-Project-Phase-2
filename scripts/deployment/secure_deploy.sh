#!/bin/bash

# AstraTrade Secure Deployment Script
# Ensures environment variables are set before deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 AstraTrade Secure Deployment${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to check if environment variable is set
check_env_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo -e "${RED}❌ Missing required environment variable: $var_name${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $var_name is set${NC}"
        return 0
    fi
}

# Function to validate private key format
validate_private_key() {
    local key=$1
    
    # Check if it starts with 0x and has proper length
    if [[ $key =~ ^0x[0-9a-fA-F]{64}$ ]]; then
        echo -e "${GREEN}✅ Private key format is valid${NC}"
        return 0
    else
        echo -e "${RED}❌ Invalid private key format. Expected: 0x followed by 64 hex characters${NC}"
        return 1
    fi
}

# Function to validate account address format
validate_account_address() {
    local addr=$1
    
    # Check if it starts with 0x and has proper length (between 40-66 chars for Starknet)
    if [[ $addr =~ ^0x[0-9a-fA-F]{40,66}$ ]]; then
        echo -e "${GREEN}✅ Account address format is valid${NC}"
        return 0
    else
        echo -e "${RED}❌ Invalid account address format. Expected: 0x followed by 40-66 hex characters${NC}"
        return 1
    fi
}

echo -e "${YELLOW}📋 Checking environment variables...${NC}"

# Check required environment variables
ENV_CHECK_FAILED=0

if ! check_env_var "STARKNET_PRIVATE_KEY"; then
    ENV_CHECK_FAILED=1
fi

if ! check_env_var "STARKNET_ACCOUNT_ADDRESS"; then
    ENV_CHECK_FAILED=1
fi

# Validate formats if variables are set
if [ ! -z "$STARKNET_PRIVATE_KEY" ]; then
    if ! validate_private_key "$STARKNET_PRIVATE_KEY"; then
        ENV_CHECK_FAILED=1
    fi
fi

if [ ! -z "$STARKNET_ACCOUNT_ADDRESS" ]; then
    if ! validate_account_address "$STARKNET_ACCOUNT_ADDRESS"; then
        ENV_CHECK_FAILED=1
    fi
fi

if [ $ENV_CHECK_FAILED -eq 1 ]; then
    echo ""
    echo -e "${RED}❌ Environment validation failed${NC}"
    echo ""
    echo -e "${YELLOW}💡 To fix this:${NC}"
    echo -e "1. Generate a new Starknet account at: ${BLUE}https://starknet-faucet.vercel.app/${NC}"
    echo -e "2. Set your environment variables:"
    echo -e "   ${GREEN}export STARKNET_PRIVATE_KEY='0x[your_private_key]'${NC}"
    echo -e "   ${GREEN}export STARKNET_ACCOUNT_ADDRESS='0x[your_account_address]'${NC}"
    echo -e "3. Source your environment file:"
    echo -e "   ${GREEN}source .env.deployment.local${NC}"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All environment variables validated${NC}"
echo ""

# Parse command line arguments
NETWORK="sepolia"
OWNER_ADDRESS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --owner)
            OWNER_ADDRESS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--network sepolia|mainnet] [--owner ADDRESS]"
            echo ""
            echo "Options:"
            echo "  --network    Target network (default: sepolia)"
            echo "  --owner      Contract owner address (default: STARKNET_ACCOUNT_ADDRESS)"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Set default owner to account address if not provided
if [ -z "$OWNER_ADDRESS" ]; then
    OWNER_ADDRESS="$STARKNET_ACCOUNT_ADDRESS"
fi

echo -e "${YELLOW}🎯 Deployment Configuration:${NC}"
echo -e "   Network: ${GREEN}$NETWORK${NC}"
echo -e "   Owner: ${GREEN}$OWNER_ADDRESS${NC}"
echo ""

# Confirm deployment
echo -e "${YELLOW}⚠️  This will deploy contracts to $NETWORK network${NC}"
echo -e "${YELLOW}   Make sure you have sufficient balance for gas fees${NC}"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🛑 Deployment cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 Starting deployment...${NC}"

# Create logs directory
mkdir -p deployment_logs

# Execute Python deployment script
python3 scripts/deploy_contracts.py \
    --network "$NETWORK" \
    --owner "$OWNER_ADDRESS" \
    2>&1 | tee "deployment_logs/deployment_$(date +%Y%m%d_%H%M%S).log"

DEPLOYMENT_RESULT=${PIPESTATUS[0]}

if [ $DEPLOYMENT_RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo -e "1. Verify contracts on block explorer"
    echo -e "2. Update frontend configuration"
    echo -e "3. Test contract interactions"
    echo -e "4. Fund paymaster for gasless transactions"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo -e "Check the deployment logs for details"
    echo ""
    exit 1
fi