#!/usr/bin/env python3
"""
AstraTrade Smart Contract Deployment Script
Deploys Paymaster, Vault, and Exchange contracts to Starknet Sepolia
"""

import asyncio
import json
import os
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract

# Load deployment account info
with open("deployment_account.json", "r") as f:
    deployment_account = json.load(f)

# RPC endpoint
rpc_url = "https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_8/R9ppBBhFDUo9CN8zsHvnqFz7IQcRTaJV"

# Connect to Starknet Sepolia
client = FullNodeClient(node_url=rpc_url, chain=StarknetChainId.SEPOLIA)

# Account setup
private_key = int(os.environ.get("PRIVATE_KEY"), 0)  # Get private key from environment
account_address = int(deployment_account["deployment"]["address"], 16)
key_pair = KeyPair(private_key=private_key, public_key=int(deployment_account["variant"]["owner"], 16))
account = Account(
    client=client,
    address=account_address,
    key_pair=key_pair,
    chain=StarknetChainId.SEPOLIA,
)

async def deploy_contracts():
    print("🚀 Deploying AstraTrade contracts to Starknet Sepolia...")
    
    # Read compiled contract files
    with open("target/dev/astratrade_contracts_AstraTradePaymaster.contract_class.json", "r") as f:
        paymaster_compiled = json.load(f)
        
    with open("target/dev/astratrade_contracts_AstraTradeVault.contract_class.json", "r") as f:
        vault_compiled = json.load(f)
        
    with open("target/dev/astratrade_contracts_AstraTradeExchange.contract_class.json", "r") as f:
        exchange_compiled = json.load(f)
    
    # Deploy Paymaster contract
    print(" Deploying Paymaster contract...")
    paymaster_declare_result = await account.declare_v2(
        compiled_contract=json.dumps(paymaster_compiled),
        max_fee=int(1e16)
    )
    await paymaster_declare_result.wait_for_acceptance()
    print(f"✅ Paymaster class declared: {hex(paymaster_declare_result.class_hash)}")
    
    paymaster_deploy_result = await account.deploy_v1(
        class_hash=paymaster_declare_result.class_hash,
        constructor_calldata=[account_address],  # owner
        max_fee=int(1e16)
    )
    await paymaster_deploy_result.wait_for_acceptance()
    print(f"✅ Paymaster deployed: {hex(paymaster_deploy_result.deployed_contract.address)}")
    
    # Deploy Vault contract
    print(" Deploying Vault contract...")
    vault_declare_result = await account.declare_v2(
        compiled_contract=json.dumps(vault_compiled),
        max_fee=int(1e16)
    )
    await vault_declare_result.wait_for_acceptance()
    print(f"✅ Vault class declared: {hex(vault_declare_result.class_hash)}")
    
    vault_deploy_result = await account.deploy_v1(
        class_hash=vault_declare_result.class_hash,
        constructor_calldata=[account_address],  # owner
        max_fee=int(1e16)
    )
    await vault_deploy_result.wait_for_acceptance()
    print(f"✅ Vault deployed: {hex(vault_deploy_result.deployed_contract.address)}")
    
    # Deploy Exchange contract
    print(" Deploying Exchange contract...")
    exchange_declare_result = await account.declare_v2(
        compiled_contract=json.dumps(exchange_compiled),
        max_fee=int(1e16)
    )
    await exchange_declare_result.wait_for_acceptance()
    print(f"✅ Exchange class declared: {hex(exchange_declare_result.class_hash)}")
    
    exchange_deploy_result = await account.deploy_v1(
        class_hash=exchange_declare_result.class_hash,
        constructor_calldata=[account_address],  # owner
        max_fee=int(1e16)
    )
    await exchange_deploy_result.wait_for_acceptance()
    print(f"✅ Exchange deployed: {hex(exchange_deploy_result.deployed_contract.address)}")
    
    # Save deployment results
    deployment_results = {
        "paymaster": {
            "address": hex(paymaster_deploy_result.deployed_contract.address),
            "class_hash": hex(paymaster_declare_result.class_hash)
        },
        "vault": {
            "address": hex(vault_deploy_result.deployed_contract.address),
            "class_hash": hex(vault_declare_result.class_hash)
        },
        "exchange": {
            "address": hex(exchange_deploy_result.deployed_contract.address),
            "class_hash": hex(exchange_declare_result.class_hash)
        }
    }
    
    with open("live_deployment_results.json", "w") as f:
        json.dump(deployment_results, f, indent=2)
    
    print("\n🎉 All contracts deployed successfully!")
    print(f"📝 Deployment results saved to live_deployment_results.json")
    return deployment_results

if __name__ == "__main__":
    asyncio.run(deploy_contracts())