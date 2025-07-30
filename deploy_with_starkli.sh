#!/bin/bash

# Set environment variables
export RPC_URL="https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_8/R9ppBBhFDUo9CN8zsHvnqFz7IQcRTaJV"
export ACCOUNT_ADDRESS="0x05715b600c38f3bfa539281865cf8d7b9fe998d79a2cf181c70effcb182752f7"

echo "🚀 Deploying AstraTrade contracts to Starknet Sepolia..."

# Declare Paymaster contract
echo " Declaring Paymaster contract..."
PAYMASTER_CLASS_HASH=$(starkli declare target/dev/astratrade_contracts_AstraTradePaymaster.contract_class.json \
  --rpc $RPC_URL \
  --account account.json \
  --private-key 0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e \
  --watch)

echo "✅ Paymaster class hash: $PAYMASTER_CLASS_HASH"

# Deploy Paymaster contract
echo " Deploying Paymaster contract..."
PAYMASTER_ADDRESS=$(starkli deploy $PAYMASTER_CLASS_HASH $ACCOUNT_ADDRESS \
  --rpc $RPC_URL \
  --account account.json \
  --private-key 0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e \
  --watch)

echo "✅ Paymaster deployed at: $PAYMASTER_ADDRESS"

# Declare Vault contract
echo " Declaring Vault contract..."
VAULT_CLASS_HASH=$(starkli declare target/dev/astratrade_contracts_AstraTradeVault.contract_class.json \
  --rpc $RPC_URL \
  --account account.json \
  --private-key 0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e \
  --watch)

echo "✅ Vault class hash: $VAULT_CLASS_HASH"

# Deploy Vault contract
echo " Deploying Vault contract..."
VAULT_ADDRESS=$(starkli deploy $VAULT_CLASS_HASH $ACCOUNT_ADDRESS \
  --rpc $RPC_URL \
  --account account.json \
  --private-key 0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e \
  --watch)

echo "✅ Vault deployed at: $VAULT_ADDRESS"

# Declare Exchange contract
echo " Declaring Exchange contract..."
EXCHANGE_CLASS_HASH=$(starkli declare target/dev/astratrade_contracts_AstraTradeExchange.contract_class.json \
  --rpc $RPC_URL \
  --account account.json \
  --private-key 0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e \
  --watch)

echo "✅ Exchange class hash: $EXCHANGE_CLASS_HASH"

# Deploy Exchange contract
echo " Deploying Exchange contract..."
EXCHANGE_ADDRESS=$(starkli deploy $EXCHANGE_CLASS_HASH $ACCOUNT_ADDRESS \
  --rpc $RPC_URL \
  --account account.json \
  --private-key 0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e \
  --watch)

echo "✅ Exchange deployed at: $EXCHANGE_ADDRESS"

# Save deployment results
cat > live_deployment_results.json << EOF
{
  "paymaster": {
    "address": "$PAYMASTER_ADDRESS",
    "class_hash": "$PAYMASTER_CLASS_HASH"
  },
  "vault": {
    "address": "$VAULT_ADDRESS",
    "class_hash": "$VAULT_CLASS_HASH"
  },
  "exchange": {
    "address": "$EXCHANGE_ADDRESS",
    "class_hash": "$EXCHANGE_CLASS_HASH"
  }
}
EOF

echo ""
echo "🎉 All contracts deployed successfully!"
echo "📝 Deployment results saved to live_deployment_results.json"