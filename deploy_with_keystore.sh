#!/bin/bash

# Set environment variables
export STARKNET_RPC="https://starknet-sepolia.public.blastapi.io"

# Create keystore file from private key
echo "Creating keystore file..."
echo "0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e" | starkli signer keystore from-key ~/deployment_keystore.json || {
    echo "Keystore creation failed, trying alternative method..."
    # Alternative approach: use environment variable
    export STARKNET_PRIVATE_KEY="0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e"
}

echo "Declaring AstraTradePaymaster contract..."
starkli declare --account deployment_account.json target/dev/astratrade_contracts_AstraTradePaymaster.contract_class.json --keystore ~/deployment_keystore.json || {
    echo "Declaration with keystore failed, trying with private key..."
    starkli declare --account deployment_account.json target/dev/astratrade_contracts_AstraTradePaymaster.contract_class.json
}

echo "Declaring AstraTradeVault contract..."
starkli declare --account deployment_account.json target/dev/astratrade_contracts_AstraTradeVault.contract_class.json --keystore ~/deployment_keystore.json || {
    echo "Declaration with keystore failed, trying with private key..."
    starkli declare --account deployment_account.json target/dev/astratrade_contracts_AstraTradeVault.contract_class.json
}