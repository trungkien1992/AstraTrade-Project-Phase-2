#!/usr/bin/env python3
"""
Real AstraTrade Contract Deployment using starknet-py
Deploy to Starknet Sepolia testnet with provided private key
"""

import asyncio
import json
import os
from pathlib import Path

async def deploy_with_starknet_py():
    """Deploy contracts using starknet-py"""
    
    print("🚀 AstraTrade Contract Deployment - starknet-py")
    print("=" * 50)
    
    private_key = "0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e"
    account_address = "0x05715B600c38f3BFA539281865Cf8d7B9fE998D79a2CF181c70eFFCb182752F7"
    rpc_url = "https://starknet-sepolia.public.blastapi.io"
    
    try:
        from starknet_py.net.full_node_client import FullNodeClient
        from starknet_py.net.account.account import Account
        from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
        from starknet_py.contract import Contract
        from starknet_py.net.models import StarknetChainId
        
        print("✅ Starknet-py imported successfully")
        
        # Create client
        client = FullNodeClient(node_url=rpc_url)
        print(f"✅ Connected to Sepolia: {rpc_url}")
        
        # Create signer
        key_pair = StarkCurveSigner(
            account_address=account_address,
            private_key=int(private_key, 16),
            chain_id=StarknetChainId.TESTNET
        )
        print("✅ Signer created")
        
        # Create account
        account = Account(
            address=account_address,
            client=client,
            signer=key_pair,
            chain=StarknetChainId.TESTNET
        )
        print("✅ Account created")
        
        # Check compiled contracts exist
        paymaster_path = Path("target/dev/astratrade_contracts_AstraTradePaymaster.contract_class.json")
        vault_path = Path("target/dev/astratrade_contracts_AstraTradeVault.contract_class.json")
        
        print(f"📋 Checking contracts...")
        print(f"   Paymaster: {paymaster_path.exists()}")
        print(f"   Vault: {vault_path.exists()}")
        
        if not paymaster_path.exists() or not vault_path.exists():
            print("❌ Contract files not found. Compiling first...")
            import subprocess
            result = subprocess.run(["scarb", "build"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Compilation failed: {result.stderr}")
                return
            print("✅ Contracts compiled")
        
        # Deploy Paymaster
        print("\n1️⃣ Deploying Paymaster Contract...")
        
        with open(paymaster_path, 'r') as f:
            paymaster_compiled = json.load(f)
        
        print("   📦 Contract loaded, attempting deployment...")
        
        # Deploy contract
        deploy_result = await Contract.deploy_contract(
            account=account,
            class_hash=None,  # Will be computed from compiled_contract
            abi=paymaster_compiled.get("abi", []),
            compiled_contract=paymaster_compiled,
            constructor_calldata=[int(account_address, 16)],  # owner parameter
        )
        
        paymaster_address = hex(deploy_result.deployed_contract.address)
        print(f"   🎉 Paymaster deployed successfully!")
        print(f"   📍 Address: {paymaster_address}")
        print(f"   🔍 Verify: https://sepolia.starkscan.co/contract/{paymaster_address}")
        
        # Deploy Vault
        print("\n2️⃣ Deploying Vault Contract...")
        
        with open(vault_path, 'r') as f:
            vault_compiled = json.load(f)
        
        deploy_result_vault = await Contract.deploy_contract(
            account=account,
            class_hash=None,
            abi=vault_compiled.get("abi", []),
            compiled_contract=vault_compiled,
            constructor_calldata=[int(account_address, 16)],  # owner parameter
        )
        
        vault_address = hex(deploy_result_vault.deployed_contract.address)
        print(f"   🎉 Vault deployed successfully!")
        print(f"   📍 Address: {vault_address}")
        print(f"   🔍 Verify: https://sepolia.starkscan.co/contract/{vault_address}")
        
        # Save deployment results
        deployment_data = {
            "network": "sepolia",
            "timestamp": "2025-07-30T05:00:00Z",
            "deployment_status": "SUCCESS",
            "account_address": account_address,
            "contracts": {
                "paymaster": {
                    "address": paymaster_address,
                    "explorer": f"https://sepolia.starkscan.co/contract/{paymaster_address}",
                    "source": "src/contracts/paymaster.cairo"
                },
                "vault": {
                    "address": vault_address,
                    "explorer": f"https://sepolia.starkscan.co/contract/{vault_address}",
                    "source": "src/contracts/vault.cairo"
                }
            }
        }
        
        with open('REAL_DEPLOYMENT_SUCCESS.json', 'w') as f:
            json.dump(deployment_data, f, indent=2)
        
        print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"📋 Both contracts deployed to Starknet Sepolia")
        print(f"💾 Results saved to REAL_DEPLOYMENT_SUCCESS.json")
        
        return deployment_data
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure starknet-py is installed in virtual environment")
        return None
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return None

async def main():
    """Main deployment function"""
    
    # Ensure we're in the virtual environment
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Not in virtual environment. Activating...")
        import subprocess
        
        # Try to run with venv activated
        cmd = "source deployment_env/bin/activate && python3 python_deploy.py"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
        return
    
    # Deploy contracts
    result = await deploy_with_starknet_py()
    
    if result:
        print(f"\n✅ REAL DEPLOYMENT COMPLETE!")
        print(f"🔍 Check contracts on StarkScan:")
        for name, contract in result['contracts'].items():
            print(f"   {name.title()}: {contract['explorer']}")
    else:
        print(f"\n❌ Deployment failed")

if __name__ == "__main__":
    asyncio.run(main())