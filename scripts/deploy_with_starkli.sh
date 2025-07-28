#!/bin/bash

# AstraTrade Contract Deployment Script using Starkli
# Deploys all 4 contracts to Starknet Sepolia testnet

set -e

# Load environment variables
if [ -f ".env.deployment" ]; then
    source .env.deployment
    echo "✅ Environment loaded"
else
    echo "❌ .env.deployment file not found"
    exit 1
fi

# Verify required environment variables
if [ -z "$STARKNET_PRIVATE_KEY" ] || [ -z "$STARKNET_ACCOUNT_ADDRESS" ]; then
    echo "❌ Missing required environment variables"
    echo "Required: STARKNET_PRIVATE_KEY, STARKNET_ACCOUNT_ADDRESS"
    exit 1
fi

echo "🚀 AstraTrade Contract Deployment Starting..."
echo "Network: ${STARKNET_NETWORK}"
echo "Account: ${STARKNET_ACCOUNT_ADDRESS}"
echo "RPC: ${STARKNET_RPC_URL}"
echo "=================================================="

# Create deployment logs directory
mkdir -p deployment_logs

# Function to compile contract
compile_contract() {
    local contract_name=$1
    echo "📦 Compiling $contract_name..."
    
    cd src/contracts/$contract_name
    scarb build
    cd ../../..
    
    if [ $? -eq 0 ]; then
        echo "✅ $contract_name compiled successfully"
        return 0
    else
        echo "❌ $contract_name compilation failed"
        return 1
    fi
}

# Function to declare contract
declare_contract() {
    local contract_name=$1
    local sierra_dir="src/contracts/$contract_name/target/dev"
    
    echo "📤 Declaring $contract_name..."
    
    # Find the actual sierra file by pattern
    local actual_sierra=$(find "$sierra_dir" -name "*contract_class.json" | head -1)
    
    if [ -z "$actual_sierra" ]; then
        echo "❌ Sierra file not found for $contract_name in $sierra_dir"
        return 1
    fi
    
    echo "Using sierra file: $actual_sierra"
    
    # Declare the contract
    local declare_result=$(starkli declare \
        --network sepolia \
        --account $STARKNET_ACCOUNT_ADDRESS \
        --private-key $STARKNET_PRIVATE_KEY \
        --compiler-version 2.8.0 \
        "$actual_sierra" 2>&1)
    
    if echo "$declare_result" | grep -q "Class hash declared"; then
        local class_hash=$(echo "$declare_result" | grep "Class hash declared" | awk '{print $NF}')
        echo "✅ $contract_name declared with class hash: $class_hash"
        echo "$class_hash"
        return 0
    elif echo "$declare_result" | grep -q "already been declared"; then
        local class_hash=$(echo "$declare_result" | grep -o "0x[a-fA-F0-9]\{64\}")
        echo "✅ $contract_name already declared with class hash: $class_hash"
        echo "$class_hash"
        return 0
    else
        echo "❌ Failed to declare $contract_name"
        echo "$declare_result"
        return 1
    fi
}

# Function to deploy contract
deploy_contract() {
    local contract_name=$1
    local class_hash=$2
    shift 2
    local constructor_args=("$@")
    
    echo "🚀 Deploying $contract_name..."
    echo "Class hash: $class_hash"
    echo "Constructor args: ${constructor_args[*]}"
    
    local deploy_cmd="starkli deploy \
        --network sepolia \
        --account $STARKNET_ACCOUNT_ADDRESS \
        --private-key $STARKNET_PRIVATE_KEY \
        $class_hash"
    
    # Add constructor arguments if provided
    if [ ${#constructor_args[@]} -gt 0 ]; then
        deploy_cmd="$deploy_cmd ${constructor_args[*]}"
    fi
    
    echo "Executing: $deploy_cmd"
    local deploy_result=$($deploy_cmd 2>&1)
    
    if echo "$deploy_result" | grep -q "Contract deployed:"; then
        local contract_address=$(echo "$deploy_result" | grep "Contract deployed:" | awk '{print $NF}')
        echo "✅ $contract_name deployed at: $contract_address"
        echo "$contract_address"
        return 0
    else
        echo "❌ Failed to deploy $contract_name"
        echo "$deploy_result"
        return 1
    fi
}

# Function to convert string to felt252 (hex)
string_to_felt() {
    local str=$1
    python3 -c "
import sys
s = sys.argv[1]
encoded = s.encode('utf-8')
if len(encoded) > 31:
    print('Error: string too long for felt252', file=sys.stderr)
    sys.exit(1)
felt_value = int.from_bytes(encoded, 'big')
print(hex(felt_value))
" "$str"
}

# Main deployment process
echo ""
echo "🔧 COMPILATION PHASE"
echo "===================="

# Compile all contracts
contracts=("achievement_nft" "points_leaderboard" "vault" "paymaster")
compiled_contracts=()

for contract in "${contracts[@]}"; do
    if compile_contract "$contract"; then
        compiled_contracts+=("$contract")
    else
        echo "⚠️ Skipping $contract due to compilation failure"
    fi
done

echo ""
echo "📤 DECLARATION PHASE"
echo "===================="

# Declare all compiled contracts
# Use files to store class hashes since associative arrays aren't available in older bash
mkdir -p temp_deployment

for contract in "${compiled_contracts[@]}"; do
    class_hash=$(declare_contract "$contract")
    if [ $? -eq 0 ] && [ -n "$class_hash" ]; then
        echo "$class_hash" > "temp_deployment/${contract}_class_hash"
        # Wait a bit between declarations
        sleep 3
    else
        echo "⚠️ Skipping deployment of $contract due to declaration failure"
        # Remove from compiled contracts array
        compiled_contracts=("${compiled_contracts[@]/$contract}")
    fi
done

echo ""
echo "🚀 DEPLOYMENT PHASE"
echo "==================="

# Deploy contracts with appropriate constructor arguments
# Use files to store deployed addresses
timestamp=$(date +%Y%m%d_%H%M%S)

# Deploy AchievementNFT
if [[ " ${compiled_contracts[*]} " =~ " achievement_nft " ]]; then
    echo ""
    echo "🎯 Deploying AchievementNFT..."
    
    class_hash=$(cat "temp_deployment/achievement_nft_class_hash")
    
    # Convert strings to felt252
    name_felt=$(string_to_felt "AstraTrade Achievements")
    symbol_felt=$(string_to_felt "ASTRA")
    base_uri_felt=$(string_to_felt "https://api.astratrade.com/nft/")
    
    address=$(deploy_contract "achievement_nft" "$class_hash" \
        "$name_felt" "$symbol_felt" "$base_uri_felt" "$STARKNET_ACCOUNT_ADDRESS")
    
    if [ $? -eq 0 ]; then
        echo "$address" > "temp_deployment/achievement_nft_address"
        sleep 5
    fi
fi

# Deploy PointsLeaderboard
if [[ " ${compiled_contracts[*]} " =~ " points_leaderboard " ]]; then
    echo ""
    echo "📈 Deploying PointsLeaderboard..."
    
    class_hash=$(cat "temp_deployment/points_leaderboard_class_hash")
    
    address=$(deploy_contract "points_leaderboard" "$class_hash" \
        "$STARKNET_ACCOUNT_ADDRESS")
    
    if [ $? -eq 0 ]; then
        echo "$address" > "temp_deployment/points_leaderboard_address"
        sleep 5
    fi
fi

# Deploy Vault
if [[ " ${compiled_contracts[*]} " =~ " vault " ]]; then
    echo ""
    echo "🏦 Deploying Vault..."
    
    class_hash=$(cat "temp_deployment/vault_class_hash")
    
    address=$(deploy_contract "vault" "$class_hash" \
        "$STARKNET_ACCOUNT_ADDRESS")
    
    if [ $? -eq 0 ]; then
        echo "$address" > "temp_deployment/vault_address"
        sleep 5
    fi
fi

# Deploy Paymaster (no constructor args)
if [[ " ${compiled_contracts[*]} " =~ " paymaster " ]]; then
    echo ""
    echo "⛽ Deploying Paymaster..."
    
    class_hash=$(cat "temp_deployment/paymaster_class_hash")
    
    address=$(deploy_contract "paymaster" "$class_hash")
    
    if [ $? -eq 0 ]; then
        echo "$address" > "temp_deployment/paymaster_address"
        sleep 5
    fi
fi

echo ""
echo "💾 SAVING DEPLOYMENT RESULTS"
echo "============================="

# Create deployment results JSON
deployment_file="deployment_logs/deployment_${timestamp}_${STARKNET_NETWORK}.json"

cat > "$deployment_file" << EOF
{
  "network": "$STARKNET_NETWORK",
  "deployer_address": "$STARKNET_ACCOUNT_ADDRESS",
  "timestamp": $(date +%s),
  "deployment_date": "$(date -Iseconds)",
  "rpc_url": "$STARKNET_RPC_URL",
  "explorer_base_url": "$EXPLORER_BASE_URL",
  "contracts": {
EOF

# Add contract deployments to JSON
first=true
for contract in "${compiled_contracts[@]}"; do
    if [ -f "temp_deployment/${contract}_address" ]; then
        if [ "$first" = false ]; then
            echo "," >> "$deployment_file"
        fi
        first=false
        
        address=$(cat "temp_deployment/${contract}_address")
        class_hash=$(cat "temp_deployment/${contract}_class_hash")
        
        cat >> "$deployment_file" << EOF
    "$contract": {
      "address": "$address",
      "class_hash": "$class_hash",
      "constructor_args": [],
      "timestamp": $(date +%s)
    }
EOF
    fi
done

cat >> "$deployment_file" << EOF
  }
}
EOF

echo "💾 Deployment results saved to: $deployment_file"

# Print deployment summary
echo ""
echo "📋 DEPLOYMENT SUMMARY"
echo "====================="
echo "Network: $STARKNET_NETWORK"
echo "Deployer: $STARKNET_ACCOUNT_ADDRESS"
echo "Timestamp: $(date)"
echo ""
echo "Deployed Contracts:"

successful_deployments=0
for contract in "${compiled_contracts[@]}"; do
    if [ -f "temp_deployment/${contract}_address" ]; then
        address=$(cat "temp_deployment/${contract}_address")
        class_hash=$(cat "temp_deployment/${contract}_class_hash")
        echo "  🔹 $contract"
        echo "    Address: $address"
        echo "    Class Hash: $class_hash"
        echo "    Explorer: ${EXPLORER_BASE_URL}/contract/$address"
        echo ""
        successful_deployments=$((successful_deployments + 1))
    fi
done

total_contracts=${#contracts[@]}

echo "📊 Results: $successful_deployments/$total_contracts contracts deployed successfully"

if [ $successful_deployments -eq $total_contracts ]; then
    echo "🎉 All contracts deployed successfully!"
    exit_code=0
else
    echo "⚠️ Some contracts failed to deploy"
    exit_code=1
fi

# Cleanup temporary files
rm -rf temp_deployment

exit $exit_code