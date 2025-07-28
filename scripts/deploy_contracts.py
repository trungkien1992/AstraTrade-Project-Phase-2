#!/usr/bin/env python3
"""
AstraTrade Smart Contract Deployment Script
Inspired by Tycoon's real_deploy_contracts.py architecture

This script automates the complete lifecycle of smart contract deployment:
1. Compile Cairo contracts using Scarb
2. Deploy contracts to Starknet (Sepolia/Mainnet)
3. Configure contract permissions and settings
4. Generate frontend configuration files
"""

import os
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
from datetime import datetime

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId  
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract


class AstraTradeDeployer:
    """Enhanced contract deployment automation for AstraTrade."""
    
    def __init__(self, network: str = "sepolia", private_key: Optional[str] = None):
        self.network = network
        
        # SECURITY: Load credentials from environment variables only
        self.private_key = private_key or os.getenv("STARKNET_PRIVATE_KEY")
        self.account_address = os.getenv("STARKNET_ACCOUNT_ADDRESS")
        
        # Validate required credentials
        if not self.private_key:
            print("❌ STARKNET_PRIVATE_KEY environment variable is required")
            print("💡 Set your private key with: export STARKNET_PRIVATE_KEY='0x...'")
            raise ValueError("Missing required STARKNET_PRIVATE_KEY")
        
        if not self.account_address:
            print("❌ STARKNET_ACCOUNT_ADDRESS environment variable is required")
            print("💡 Set your account address with: export STARKNET_ACCOUNT_ADDRESS='0x...'")
            raise ValueError("Missing required STARKNET_ACCOUNT_ADDRESS")
        
        # Network configuration
        self.networks = {
            "sepolia": {
                "rpc_url": "https://free-rpc.nethermind.io/sepolia-juno",
                "chain_id": StarknetChainId.SEPOLIA,
                "explorer": "https://sepolia.starkscan.co"
            },
            "mainnet": {
                "rpc_url": "https://alpha-mainnet.starknet.io", 
                "chain_id": StarknetChainId.MAINNET,
                "explorer": "https://starkscan.co"
            }
        }
        
        # Contract deployment info
        self.deployed_contracts = {}
        self.deployment_log = []
        
        # Initialize client and account
        self._setup_client()
    
    def _setup_client(self):
        """Initialize Starknet client and account."""
        network_config = self.networks[self.network]
        
        self.client = FullNodeClient(node_url=network_config["rpc_url"])
        
        if self.private_key and self.account_address:
            key_pair = KeyPair.from_private_key(int(self.private_key, 16))
            self.account = Account(
                address=self.account_address,
                client=self.client,
                key_pair=key_pair,
                chain=network_config["chain_id"]
            )
        else:
            print("⚠️  Warning: No private key or account address provided. Deployment will be simulated.")
            self.account = None
    
    async def compile_contracts(self) -> bool:
        """Compile all Cairo contracts using Scarb."""
        print("🔨 Compiling smart contracts...")
        
        try:
            # Change to project root directory
            original_dir = os.getcwd()
            project_root = Path(__file__).parent.parent
            os.chdir(project_root)
            
            # Run scarb build
            result = subprocess.run(
                ["scarb", "build"],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Contract compilation successful!")
            self.deployment_log.append({
                "step": "compilation",
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "output": result.stdout
            })
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Compilation failed: {e.stderr}")
            self.deployment_log.append({
                "step": "compilation", 
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "error": e.stderr
            })
            return False
        finally:
            os.chdir(original_dir)
    
    async def deploy_paymaster(self, owner_address: str) -> Optional[str]:
        """Deploy the AstraTrade Paymaster contract."""
        print("🚀 Deploying Paymaster contract...")
        
        if not self.account:
            print("⚠️  Simulating Paymaster deployment (no account configured)")
            return "0x1234567890123456789012345678901234567890"
        
        try:
            # Load compiled contract
            contract_path = "target/dev/astratrade_contracts_AstraTradePaymaster.sierra.json"
            
            with open(contract_path) as f:
                contract_definition = json.load(f)
            
            # Deploy contract
            deploy_result = await Contract.deploy_contract(
                account=self.account,
                class_hash=None,  # Will be computed from definition
                abi=contract_definition["abi"],
                bytecode=contract_definition["sierra_program"],
                constructor_calldata=[int(owner_address, 16)]
            )
            
            paymaster_address = hex(deploy_result.deployed_contract.address)
            self.deployed_contracts["paymaster"] = {
                "address": paymaster_address,
                "transaction_hash": hex(deploy_result.hash),
                "block_number": deploy_result.block_number
            }
            
            print(f"✅ Paymaster deployed at: {paymaster_address}")
            
            self.deployment_log.append({
                "step": "paymaster_deployment",
                "status": "success", 
                "timestamp": datetime.now().isoformat(),
                "contract_address": paymaster_address,
                "transaction_hash": hex(deploy_result.hash)
            })
            
            return paymaster_address
            
        except Exception as e:
            print(f"❌ Paymaster deployment failed: {str(e)}")
            self.deployment_log.append({
                "step": "paymaster_deployment",
                "status": "failed",
                "timestamp": datetime.now().isoformat(), 
                "error": str(e)
            })
            return None
    
    async def deploy_vault(self, owner_address: str) -> Optional[str]:
        """Deploy the AstraTrade Vault contract."""
        print("🏦 Deploying Vault contract...")
        
        if not self.account:
            print("⚠️  Simulating Vault deployment (no account configured)")
            return "0x0987654321098765432109876543210987654321"
        
        try:
            # Load compiled contract
            contract_path = "target/dev/astratrade_contracts_AstraTradeVault.sierra.json"
            
            with open(contract_path) as f:
                contract_definition = json.load(f)
            
            # Deploy contract
            deploy_result = await Contract.deploy_contract(
                account=self.account,
                class_hash=None,
                abi=contract_definition["abi"],
                bytecode=contract_definition["sierra_program"],
                constructor_calldata=[int(owner_address, 16)]
            )
            
            vault_address = hex(deploy_result.deployed_contract.address)
            self.deployed_contracts["vault"] = {
                "address": vault_address,
                "transaction_hash": hex(deploy_result.hash),
                "block_number": deploy_result.block_number
            }
            
            print(f"✅ Vault deployed at: {vault_address}")
            
            self.deployment_log.append({
                "step": "vault_deployment",
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "contract_address": vault_address,
                "transaction_hash": hex(deploy_result.hash)
            })
            
            return vault_address
            
        except Exception as e:
            print(f"❌ Vault deployment failed: {str(e)}")
            self.deployment_log.append({
                "step": "vault_deployment",
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            return None
    
    async def configure_contracts(self):
        """Configure deployed contracts with proper permissions."""
        print("⚙️  Configuring contract permissions...")
        
        if not self.account or not all(k in self.deployed_contracts for k in ["paymaster", "vault"]):
            print("⚠️  Skipping configuration (contracts not deployed or no account)")
            return
        
        try:
            paymaster_address = self.deployed_contracts["paymaster"]["address"]
            vault_address = self.deployed_contracts["vault"]["address"]
            
            # Example: Add ETH as supported token in both contracts
            eth_token_address = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
            
            calls = [
                Call(
                    to_addr=int(paymaster_address, 16),
                    selector="add_supported_token",
                    calldata=[int(eth_token_address, 16)]
                ),
                Call(
                    to_addr=int(vault_address, 16),
                    selector="add_supported_token", 
                    calldata=[int(eth_token_address, 16)]
                )
            ]
            
            # Execute multicall
            transaction = await self.account.execute(calls=calls)
            
            print(f"✅ Configuration complete. Transaction: {hex(transaction.transaction_hash)}")
            
            self.deployment_log.append({
                "step": "configuration",
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "transaction_hash": hex(transaction.transaction_hash)
            })
            
        except Exception as e:
            print(f"❌ Configuration failed: {str(e)}")
            self.deployment_log.append({
                "step": "configuration",
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
    
    def generate_frontend_config(self):
        """Generate Dart configuration file for Flutter frontend."""
        print("📱 Generating frontend configuration...")
        
        config_content = f'''// GENERATED FILE - DO NOT EDIT MANUALLY
// Generated by deploy_contracts.py on {datetime.now().isoformat()}

class ContractConfig {{
  // Network Configuration
  static const String network = '{self.network}';
  static const String explorerUrl = '{self.networks[self.network]["explorer"]}';
  
  // Contract Addresses
  static const String paymasterAddress = '{self.deployed_contracts.get("paymaster", {}).get("address", "0x0")}';
  static const String vaultAddress = '{self.deployed_contracts.get("vault", {}).get("address", "0x0")}';
  
  // Contract ABIs (simplified for key functions)
  static const List<Map<String, dynamic>> paymasterAbi = [
    {{
      "name": "sponsor_transaction",
      "type": "function",
      "inputs": [
        {{"name": "user", "type": "ContractAddress"}},
        {{"name": "gas_fee", "type": "u256"}}
      ],
      "outputs": [{{"name": "success", "type": "bool"}}]
    }},
    {{
      "name": "get_user_allowance", 
      "type": "function",
      "inputs": [{{"name": "user", "type": "ContractAddress"}}],
      "outputs": [{{"name": "allowance", "type": "u256"}}]
    }}
  ];
  
  static const List<Map<String, dynamic>> vaultAbi = [
    {{
      "name": "deposit",
      "type": "function", 
      "inputs": [
        {{"name": "token", "type": "ContractAddress"}},
        {{"name": "amount", "type": "u256"}}
      ]
    }},
    {{
      "name": "withdraw",
      "type": "function",
      "inputs": [
        {{"name": "token", "type": "ContractAddress"}},
        {{"name": "amount", "type": "u256"}}
      ]
    }},
    {{
      "name": "get_balance",
      "type": "function",
      "inputs": [
        {{"name": "user", "type": "ContractAddress"}},
        {{"name": "token", "type": "ContractAddress"}}
      ],
      "outputs": [{{"name": "balance", "type": "u256"}}]
    }}
  ];
  
  // Deployment Information
  static const Map<String, dynamic> deploymentInfo = {{
    'timestamp': '{datetime.now().isoformat()}',
    'network': '{self.network}',
    'contracts': {json.dumps(self.deployed_contracts, indent=4)}
  }};
}}
'''
        
        # Write to Flutter lib directory
        config_path = Path("astratrade_app/lib/config/contract_config.dart")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Frontend configuration generated: {config_path}")
        
        self.deployment_log.append({
            "step": "frontend_config_generation",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "config_path": str(config_path)
        })
    
    def save_deployment_log(self):
        """Save detailed deployment log for future reference."""
        log_path = Path(f"deployment_logs/deployment_{self.network}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        deployment_summary = {
            "network": self.network,
            "timestamp": datetime.now().isoformat(),
            "deployed_contracts": self.deployed_contracts,
            "deployment_steps": self.deployment_log,
            "explorer_links": {
                name: f"{self.networks[self.network]['explorer']}/contract/{contract['address']}"
                for name, contract in self.deployed_contracts.items()
            }
        }
        
        with open(log_path, 'w') as f:
            json.dump(deployment_summary, f, indent=2)
        
        print(f"📋 Deployment log saved: {log_path}")
    
    async def deploy_all(self, owner_address: str):
        """Execute complete deployment workflow."""
        print(f"🚀 Starting AstraTrade deployment to {self.network}...")
        print(f"🔑 Owner address: {owner_address}")
        print("=" * 50)
        
        # Step 1: Compile contracts
        if not await self.compile_contracts():
            print("❌ Deployment aborted due to compilation failure")
            return False
        
        # Step 2: Deploy contracts
        paymaster_addr = await self.deploy_paymaster(owner_address)
        vault_addr = await self.deploy_vault(owner_address)
        
        if not paymaster_addr or not vault_addr:
            print("❌ Deployment aborted due to contract deployment failure")
            return False
        
        # Step 3: Configure contracts
        await self.configure_contracts()
        
        # Step 4: Generate frontend config
        self.generate_frontend_config()
        
        # Step 5: Save deployment log
        self.save_deployment_log()
        
        print("=" * 50)
        print("🎉 AstraTrade deployment completed successfully!")
        print(f"📱 Paymaster: {paymaster_addr}")
        print(f"🏦 Vault: {vault_addr}")
        print(f"🔍 Explorer: {self.networks[self.network]['explorer']}")
        
        return True


async def main():
    """Main deployment script entry point."""
    parser = argparse.ArgumentParser(description="Deploy AstraTrade smart contracts")
    parser.add_argument("--network", choices=["sepolia", "mainnet"], default="sepolia",
                       help="Target network for deployment")
    parser.add_argument("--owner", required=True,
                       help="Contract owner address")
    parser.add_argument("--private-key", 
                       help="Private key for deployment account (can also use STARKNET_PRIVATE_KEY env var)")
    
    args = parser.parse_args()
    
    # Create deployer
    deployer = AstraTradeDeployer(
        network=args.network,
        private_key=args.private_key
    )
    
    # Execute deployment
    success = await deployer.deploy_all(args.owner)
    
    if success:
        print("✅ Deployment completed successfully!")
        return 0
    else:
        print("❌ Deployment failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))