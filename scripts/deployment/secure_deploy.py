#!/usr/bin/env python3
"""
Secure Contract Deployment Script for AstraTrade Project
Deploys all 4 contracts (AchievementNFT, PointsLeaderboard, Vault, Paymaster) to Starknet
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import subprocess
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
from starknet_py.net.client_models import Call
from starknet_py.cairo.felt import encode_shortstring


class SecureDeployer:
    """Secure contract deployment manager"""
    
    def __init__(self, env_file: str = ".env.deployment"):
        self.env_file = env_file
        self.load_environment()
        self.setup_client()
        self.deployment_results = {}
        
    def load_environment(self):
        """Load environment variables from file"""
        env_path = Path(self.env_file)
        if not env_path.exists():
            raise FileNotFoundError(f"Environment file {self.env_file} not found")
            
        # Load environment variables
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    
        # Validate required variables
        required_vars = [
            'STARKNET_PRIVATE_KEY',
            'STARKNET_ACCOUNT_ADDRESS', 
            'STARKNET_NETWORK',
            'STARKNET_RPC_URL'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
            
        print(f"✅ Environment loaded successfully")
        print(f"🌐 Network: {os.getenv('STARKNET_NETWORK')}")
        print(f"📍 Account: {os.getenv('STARKNET_ACCOUNT_ADDRESS')}")
        
    def setup_client(self):
        """Initialize Starknet client and account"""
        try:
            # Setup network client
            rpc_url = os.getenv('STARKNET_RPC_URL')
            self.client = GatewayClient(net=rpc_url)
            
            # Setup account
            private_key = int(os.getenv('STARKNET_PRIVATE_KEY'), 16)
            account_address = int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)
            
            key_pair = KeyPair.from_private_key(private_key)
            
            # Determine chain ID
            network = os.getenv('STARKNET_NETWORK', 'sepolia')
            chain_id = StarknetChainId.SEPOLIA if network == 'sepolia' else StarknetChainId.MAINNET
            
            self.account = Account(
                address=account_address,
                client=self.client,
                key_pair=key_pair,
                chain=chain_id
            )
            
            print(f"✅ Starknet client initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to setup client: {e}")
            sys.exit(1)
            
    def compile_contracts(self) -> bool:
        """Compile all contracts using Scarb"""
        print(f"\n🔧 Compiling contracts...")
        
        contracts = [
            'achievement_nft',
            'points_leaderboard', 
            'vault',
            'paymaster'
        ]
        
        compiled_successfully = []
        
        for contract in contracts:
            contract_dir = f"src/contracts/{contract}"
            if not Path(contract_dir).exists():
                print(f"❌ Contract directory not found: {contract_dir}")
                continue
                
            try:
                print(f"  📦 Compiling {contract}...")
                result = subprocess.run(
                    ['scarb', 'build'],
                    cwd=contract_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"    ✅ {contract} compiled successfully")
                    compiled_successfully.append(contract)
                else:
                    print(f"    ❌ {contract} compilation failed:")
                    print(f"    Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"    ❌ {contract} compilation timed out")
            except Exception as e:
                print(f"    ❌ {contract} compilation error: {e}")
                
        print(f"\n📊 Compilation Results: {len(compiled_successfully)}/{len(contracts)} contracts compiled")
        return len(compiled_successfully) == len(contracts)
        
    def get_contract_artifacts(self, contract_name: str) -> Tuple[dict, dict]:
        """Load contract class and ABI from artifacts"""
        contract_dir = f"src/contracts/{contract_name}"
        target_dir = f"{contract_dir}/target/dev"
        
        # Find contract class file
        class_files = list(Path(target_dir).glob("*.contract_class.json"))
        if not class_files:
            raise FileNotFoundError(f"No contract class file found for {contract_name}")
            
        class_file = class_files[0]
        
        with open(class_file, 'r') as f:
            contract_class = json.load(f)
            
        # Extract ABI from contract class
        abi = contract_class.get('abi', [])
        
        return contract_class, abi
        
    async def deploy_contract(self, name: str, constructor_args: List = None) -> Optional[str]:
        """Deploy a single contract"""
        try:
            print(f"\n🚀 Deploying {name}...")
            
            # Load contract artifacts
            contract_class, abi = self.get_contract_artifacts(name)
            
            # Prepare constructor arguments
            constructor_args = constructor_args or []
            
            # Deploy contract
            deployment_result = await Contract.deploy_contract(
                account=self.account,
                class_hash=None,  # Will be computed from contract_class
                abi=abi,
                constructor_args=constructor_args,
                cairo_version=1,
                compiled_contract=contract_class,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16),
                auto_fee=os.getenv('AUTO_FEE', 'true').lower() == 'true'
            )
            
            await deployment_result.wait_for_acceptance()
            
            contract_address = hex(deployment_result.deployed_contract.address)
            print(f"    ✅ {name} deployed successfully!")
            print(f"    📍 Contract Address: {contract_address}")
            print(f"    🔗 Transaction Hash: {hex(deployment_result.hash)}")
            
            # Store deployment info
            self.deployment_results[name] = {
                'address': contract_address,
                'transaction_hash': hex(deployment_result.hash),
                'constructor_args': constructor_args,
                'timestamp': int(time.time()),
                'block_number': deployment_result.block_number if hasattr(deployment_result, 'block_number') else None
            }
            
            return contract_address
            
        except Exception as e:
            print(f"    ❌ {name} deployment failed: {e}")
            return None
            
    async def deploy_all_contracts(self):
        """Deploy all contracts in correct order"""
        print(f"\n🚀 Starting deployment of all contracts...")
        
        # Define deployment order and constructor arguments
        deployments = [
            {
                'name': 'achievement_nft',
                'constructor_args': [
                    encode_shortstring("AstraTrade Achievements"),  # name
                    encode_shortstring("ASTRA"),                    # symbol
                    encode_shortstring("https://api.astratrade.com/nft/"),  # base_uri
                    int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)  # owner
                ]
            },
            {
                'name': 'points_leaderboard',
                'constructor_args': [
                    int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)  # owner
                ]
            },
            {
                'name': 'vault',
                'constructor_args': [
                    int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)  # initial_owner
                ]
            },
            {
                'name': 'paymaster',
                'constructor_args': []  # No constructor args needed
            }
        ]
        
        successful_deployments = 0
        
        for deployment in deployments:
            contract_address = await self.deploy_contract(
                deployment['name'],
                deployment['constructor_args']
            )
            
            if contract_address:
                successful_deployments += 1
                
                # Wait between deployments to avoid rate limiting
                if successful_deployments < len(deployments):
                    print(f"    ⏳ Waiting 10 seconds before next deployment...")
                    await asyncio.sleep(10)
            else:
                print(f"    ⚠️  Continuing with remaining deployments...")
                
        print(f"\n📊 Deployment Summary: {successful_deployments}/{len(deployments)} contracts deployed successfully")
        return successful_deployments == len(deployments)
        
    def save_deployment_results(self):
        """Save deployment results to file"""
        if not self.deployment_results:
            print("⚠️  No deployment results to save")
            return
            
        # Create deployment logs directory
        logs_dir = Path("deployment_logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"deployment_{timestamp}_{os.getenv('STARKNET_NETWORK', 'unknown')}.json"
        filepath = logs_dir / filename
        
        # Prepare deployment data
        deployment_data = {
            'network': os.getenv('STARKNET_NETWORK'),
            'deployer_address': os.getenv('STARKNET_ACCOUNT_ADDRESS'),
            'timestamp': int(time.time()),
            'contracts': self.deployment_results,
            'explorer_base_url': os.getenv('EXPLORER_BASE_URL', 'https://sepolia.starkscan.co')
        }
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(deployment_data, f, indent=2)
            
        print(f"💾 Deployment results saved to: {filepath}")
        
        # Print deployment summary
        print(f"\n📋 Deployment Summary:")
        print(f"Network: {deployment_data['network']}")
        print(f"Deployer: {deployment_data['deployer_address']}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(deployment_data['timestamp']))}")
        print(f"\nDeployed Contracts:")
        
        for name, info in self.deployment_results.items():
            print(f"  🔹 {name}")
            print(f"    Address: {info['address']}")
            print(f"    Tx Hash: {info['transaction_hash']}")
            
    async def verify_deployments(self):
        """Verify that deployed contracts are working"""
        print(f"\n✅ Verifying deployed contracts...")
        
        verification_results = {}
        
        for contract_name, deployment_info in self.deployment_results.items():
            try:
                print(f"  🔍 Verifying {contract_name}...")
                
                # Load contract ABI
                _, abi = self.get_contract_artifacts(contract_name)
                
                # Create contract instance
                contract = Contract(
                    address=int(deployment_info['address'], 16),
                    abi=abi,
                    provider=self.account,
                    cairo_version=1
                )
                
                # Perform basic verification based on contract type
                verification_success = await self.verify_contract_specific(contract_name, contract)
                verification_results[contract_name] = verification_success
                
                if verification_success:
                    print(f"    ✅ {contract_name} verification passed")
                else:
                    print(f"    ❌ {contract_name} verification failed")
                    
            except Exception as e:
                print(f"    ❌ {contract_name} verification error: {e}")
                verification_results[contract_name] = False
                
        successful_verifications = sum(verification_results.values())
        total_contracts = len(verification_results)
        
        print(f"\n📊 Verification Results: {successful_verifications}/{total_contracts} contracts verified")
        return successful_verifications == total_contracts
        
    async def verify_contract_specific(self, contract_name: str, contract: Contract) -> bool:
        """Perform contract-specific verification"""
        try:
            if contract_name == 'achievement_nft':
                # Verify NFT contract
                name = await contract.functions["name"].call()
                symbol = await contract.functions["symbol"].call()
                total_supply = await contract.functions["total_supply"].call()
                return name and symbol and total_supply is not None
                
            elif contract_name == 'points_leaderboard':
                # Verify leaderboard contract
                owner = await contract.functions["get_owner"].call()
                total_users = await contract.functions["get_total_users"].call()
                is_paused = await contract.functions["is_paused"].call()
                return owner and total_users is not None and is_paused is not None
                
            elif contract_name == 'vault':
                # Verify vault contract
                owner = await contract.functions["get_owner"].call()
                is_paused = await contract.functions["is_paused"].call()
                return owner and is_paused is not None
                
            elif contract_name == 'paymaster':
                # Verify minimal test contract
                dummy = await contract.functions["get_dummy"].call()
                return dummy is not None
                
            return False
            
        except Exception as e:
            print(f"      Error in specific verification: {e}")
            return False


async def main():
    """Main deployment function"""
    print("🚀 AstraTrade Contract Deployment Starting...")
    print("=" * 60)
    
    try:
        # Initialize deployer
        deployer = SecureDeployer()
        
        # Compile contracts
        if not deployer.compile_contracts():
            print("❌ Compilation failed. Aborting deployment.")
            sys.exit(1)
            
        # Deploy contracts
        deployment_success = await deployer.deploy_all_contracts()
        
        if deployment_success:
            print("\n🎉 All contracts deployed successfully!")
            
            # Save deployment results
            deployer.save_deployment_results()
            
            # Verify deployments
            verification_success = await deployer.verify_deployments()
            
            if verification_success:
                print("\n🎯 All contracts verified successfully!")
                print("✅ Deployment completed successfully!")
            else:
                print("\n⚠️  Some contracts failed verification")
                
        else:
            print("\n❌ Some contracts failed to deploy")
            deployer.save_deployment_results()  # Save partial results
            
    except KeyboardInterrupt:
        print("\n⏹️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())