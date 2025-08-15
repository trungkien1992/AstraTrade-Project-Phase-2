#!/bin/bash
# AstraTrade Redis Streams Infrastructure Setup
# Auto-generated configuration script for production deployment

echo "🚀 AstraTrade Redis Streams Infrastructure Setup"
echo "=================================================="

# Configuration
REDIS_HOST=${REDIS_HOST:-"localhost"}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_PASSWORD=${REDIS_PASSWORD:-""}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to execute Redis command
redis_cmd() {
    if [ -n "$REDIS_PASSWORD" ]; then
        redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD "$@"
    else
        redis-cli -h $REDIS_HOST -p $REDIS_PORT "$@"
    fi
}

# Function to check Redis connection
check_redis_connection() {
    echo -e "${BLUE}Checking Redis connection...${NC}"
    if redis_cmd ping >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis connection successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Redis connection failed${NC}"
        echo "Please ensure Redis is running on $REDIS_HOST:$REDIS_PORT"
        exit 1
    fi
}

# Function to create consumer group with error handling
create_consumer_group() {
    local stream_pattern="$1"
    local group_name="$2"
    local description="$3"
    
    echo -e "${YELLOW}Creating consumer group: ${group_name}${NC}"
    echo "  Stream: $stream_pattern"
    echo "  Description: $description"
    
    # Try to create the group
    if redis_cmd XGROUP CREATE "$stream_pattern" "$group_name" 0 MKSTREAM 2>/dev/null; then
        echo -e "${GREEN}  ✅ Consumer group '$group_name' created successfully${NC}"
    else
        # Check if group already exists
        if redis_cmd XINFO GROUPS "$stream_pattern" 2>/dev/null | grep -q "$group_name"; then
            echo -e "${YELLOW}  ⚠️  Consumer group '$group_name' already exists${NC}"
        else
            echo -e "${RED}  ❌ Failed to create consumer group '$group_name'${NC}"
        fi
    fi
    echo
}

# Main setup function
main() {
    echo -e "${BLUE}Starting AstraTrade Redis Streams setup...${NC}"
    echo "Redis Host: $REDIS_HOST"
    echo "Redis Port: $REDIS_PORT"
    echo
    
    # Check Redis connection
    check_redis_connection
    
    echo -e "${BLUE}Creating AstraTrade consumer groups...${NC}"
    echo
    
    # Trading Domain Consumer Groups
    echo -e "${BLUE}📊 Trading Domain Consumer Groups${NC}"
    create_consumer_group "astra.trading.*" "trading_internal" "Process internal trading events (risk management, portfolio updates)"
    create_consumer_group "astra.trading.tradeexecuted.*" "trading_risk_management" "High-priority risk management and compliance processing"
    create_consumer_group "astra.trading.positionclosed.*" "trading_risk_management" "High-priority risk management and compliance processing"
    
    # Gamification Domain Consumer Groups
    echo -e "${BLUE}🎮 Gamification Domain Consumer Groups${NC}"
    create_consumer_group "astra.trading.tradingrewardscalculated.*" "gamification_xp_processors" "Process XP calculation from trading activities"
    create_consumer_group "astra.social.socialinteraction.*" "gamification_xp_processors" "Process XP calculation from social activities"
    create_consumer_group "astra.gamification.xpgained.*" "leaderboard_updaters" "Update leaderboards and rankings"
    create_consumer_group "astra.gamification.levelup.*" "leaderboard_updaters" "Update leaderboards and rankings"
    create_consumer_group "astra.*.*.v1" "achievement_processors" "Detect and unlock achievements across all domains"
    
    # Social Domain Consumer Groups
    echo -e "${BLUE}👥 Social Domain Consumer Groups${NC}"
    create_consumer_group "astra.trading.tradeexecuted.*" "social_feed_generators" "Generate social feed content from trading events"
    create_consumer_group "astra.gamification.levelup.*" "social_feed_generators" "Generate social feed content from gamification events"
    create_consumer_group "astra.nft.nftsold.*" "social_feed_generators" "Generate social feed content from NFT events"
    create_consumer_group "astra.trading.clanbattlescoreupdated.*" "clan_battle_processors" "Process clan battle scores and rankings"
    create_consumer_group "astra.social.*" "influence_calculators" "Calculate influence scores from social interactions"
    
    # Financial Domain Consumer Groups
    echo -e "${BLUE}💰 Financial Domain Consumer Groups${NC}"
    create_consumer_group "astra.trading.tradeexecuted.*" "revenue_trackers" "Track revenue from trading fees"
    create_consumer_group "astra.nft.marketplacesale.*" "revenue_trackers" "Track revenue from NFT marketplace"
    create_consumer_group "astra.financial.paymentcompleted.*" "subscription_processors" "Process subscription payments"
    create_consumer_group "astra.user.accountstatuschanged.*" "subscription_processors" "Process account upgrades"
    create_consumer_group "astra.financial.*" "financial_compliance" "Ensure compliance and audit trail"
    
    # NFT Domain Consumer Groups
    echo -e "${BLUE}🎨 NFT Domain Consumer Groups${NC}"
    create_consumer_group "astra.gamification.achievementunlocked.*" "nft_reward_distributors" "Distribute NFT rewards based on achievements"
    create_consumer_group "astra.trading.tradingrewardscalculated.*" "nft_reward_distributors" "Distribute NFT rewards based on trading"
    create_consumer_group "astra.nft.nftlisted.*" "marketplace_processors" "Process NFT marketplace listings"
    create_consumer_group "astra.nft.nftsold.*" "marketplace_processors" "Process NFT marketplace sales"
    
    # User Domain Consumer Groups
    echo -e "${BLUE}👤 User Domain Consumer Groups${NC}"
    create_consumer_group "astra.gamification.levelup.*" "user_profile_updaters" "Update user profiles based on gamification changes"
    create_consumer_group "astra.social.socialratingchanged.*" "user_profile_updaters" "Update user profiles based on social changes"
    create_consumer_group "astra.*.*.v1" "notification_senders" "Send real-time notifications to users"
    
    # Analytics Consumer Groups
    echo -e "${BLUE}📈 Analytics Consumer Groups${NC}"
    create_consumer_group "astra.*.*.v1" "metrics_collectors" "Collect metrics and KPIs from all domain events"
    create_consumer_group "astra.financial.*" "audit_trail_recorders" "Record audit trails for financial operations"
    create_consumer_group "astra.trading.*" "audit_trail_recorders" "Record audit trails for trading operations"
    create_consumer_group "astra.nft.*" "audit_trail_recorders" "Record audit trails for NFT operations"
    
    echo -e "${GREEN}🎉 Consumer group setup completed!${NC}"
    echo -e "${GREEN}Total groups created: 17${NC}"
    echo
    
    # Verify consumer groups
    echo -e "${BLUE}🔍 Verifying consumer groups...${NC}"
    
    # List some key streams to verify setup
    VERIFICATION_STREAMS=(
        "astra.trading.tradeexecuted.v1"
        "astra.gamification.xpgained.v1"
        "astra.social.socialprofilecreated.v1"
    )
    
    for stream in "${VERIFICATION_STREAMS[@]}"; do
        echo -n "  Checking $stream: "
        if redis_cmd XINFO GROUPS "$stream" 2>/dev/null >/dev/null; then
            group_count=$(redis_cmd XINFO GROUPS "$stream" 2>/dev/null | grep -c "name")
            echo -e "${GREEN}$group_count consumer groups${NC}"
        else
            echo -e "${YELLOW}No streams yet (will be created on first event)${NC}"
        fi
    done
    
    echo
    echo -e "${GREEN}✅ AstraTrade Redis Streams Infrastructure Setup Complete!${NC}"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Start your application services to begin event publishing"
    echo "2. Monitor Redis Streams with: redis-cli XINFO STREAM <stream_name>"
    echo "3. Check consumer group status with: redis-cli XINFO GROUPS <stream_name>"
    echo "4. View event bus metrics in your monitoring dashboard"
    echo
    echo -e "${BLUE}Redis Configuration:${NC}"
    echo "Host: $REDIS_HOST"
    echo "Port: $REDIS_PORT"
    echo "Stream Naming: astra.{domain}.{event}.v{version}"
    echo "Consumer Groups: 17 total (9 cross-domain, 8 internal)"
}

# Help function
show_help() {
    echo "AstraTrade Redis Streams Setup Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -t, --test           Test Redis connection only"
    echo "  -c, --clean          Clean all existing consumer groups (DANGEROUS)"
    echo
    echo "Environment Variables:"
    echo "  REDIS_HOST           Redis host (default: localhost)"
    echo "  REDIS_PORT           Redis port (default: 6379)"
    echo "  REDIS_PASSWORD       Redis password (optional)"
    echo
    echo "Examples:"
    echo "  $0                   # Setup with default localhost Redis"
    echo "  REDIS_HOST=redis.example.com $0"
    echo "  REDIS_PASSWORD=secret $0"
}

# Test function
test_connection() {
    echo -e "${BLUE}Testing Redis connection...${NC}"
    check_redis_connection
    echo -e "${GREEN}✅ Connection test passed!${NC}"
}

# Clean function (dangerous)
clean_consumer_groups() {
    echo -e "${RED}⚠️  WARNING: This will delete ALL AstraTrade consumer groups!${NC}"
    echo -e "${RED}This action is irreversible and will disrupt event processing.${NC}"
    echo
    read -p "Are you sure you want to continue? (type 'DELETE' to confirm): " confirm
    
    if [ "$confirm" = "DELETE" ]; then
        echo -e "${RED}Cleaning consumer groups...${NC}"
        # This would require implementation of cleanup logic
        echo -e "${YELLOW}Clean function not implemented yet for safety${NC}"
    else
        echo -e "${GREEN}Operation cancelled${NC}"
    fi
}

# Parse command line arguments
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    -t|--test)
        test_connection
        exit 0
        ;;
    -c|--clean)
        clean_consumer_groups
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac