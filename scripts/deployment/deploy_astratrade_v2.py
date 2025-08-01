#!/usr/bin/env python3
"""
AstraTrade V2 Real Contract Deployment Script
Deploys Exchange V2, Vault, and Paymaster contracts to Starknet Sepolia testnet

Requirements:
- Starkli CLI installed and configured
- Valid Starknet account with sufficient ETH for deployment
- Environment variables: STARKNET_ACCOUNT, STARKNET_KEYSTORE
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

class AstraTradeDeployer:
    """Production-ready contract deployment for AstraTrade V2"""
    
    def __init__(self, network: str = "sepolia"):
        self.network = network
        self.rpc_url = self._get_rpc_url(network)
        self.deployment_data = {
            "network": network,
            "rpc_url": self.rpc_url,
            "timestamp": int(time.time()),
            "deployment_date": datetime.now().isoformat(),
            "contracts": {},
            "deployment_order": [],
            "constructor_dependencies": {}
        }
        
        # Contract deployment order (dependencies first)
        self.contracts = [
            {
                "name": "exchange_v2",
                "class_name": "AstraTradeExchangeV2", 
                "constructor_args": [],
                "description": "Exchange V2 with gamification and Extended API"
            },
            {
                "name": "vault",
                "class_name": "AstraTradeVault",
                "constructor_args": [],
                "description": "Multi-collateral vault with XP rewards"
            },
            {
                "name": "paymaster", 
                "class_name": "AstraTradePaymaster",
                "constructor_args": ["${exchange_v2_address}", "${vault_address}"],
                "description": "5-tier gasless transaction system"
            }
        ]
        
        # Create deployment logs directory
        self.logs_dir = Path("deployment_logs")
        self.logs_dir.mkdir(exist_ok=True)
        
    def _get_rpc_url(self, network: str) -> str:
        """Get RPC URL for network"""
        # Check if custom RPC is provided via environment variable
        custom_rpc = os.getenv("STARKNET_RPC")
        if custom_rpc:
            return custom_rpc
            
        rpc_urls = {
            "sepolia": "https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_8/R9ppBBhFDUo9CN8zsHvnqFz7IQcRTaJV",
            "mainnet": "https://free-rpc.nethermind.io/mainnet-juno",
            "goerli": "https://free-rpc.nethermind.io/goerli-juno"
        }
        return rpc_urls.get(network, rpc_urls["sepolia"])
        
    def run_command(self, command: List[str], description: str, timeout: int = 300) -> Dict:
        """Run a command with proper error handling"""
        print(f"🔧 {description}")
        print(f"   Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ Success")
                return {
                    "success": True,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip()
                }
            else:
                print(f"   ❌ Failed (exit code: {result.returncode})")
                print(f"   STDOUT: {result.stdout}")
                print(f"   STDERR: {result.stderr}")
                return {
                    "success": False,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "exit_code": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Command timed out after {timeout}s")
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        print("🔍 Checking deployment prerequisites...")
        
        # Check required tools
        tools = [
            (["starkli", "--version"], "Starkli CLI"),
            (["scarb", "--version"], "Scarb build tool")
        ]
        
        for command, name in tools:
            result = self.run_command(command, f"Checking {name}")
            if not result["success"]:
                print(f"   ❌ {name} not available - please install it first")
                return False
            else:
                print(f"   ✅ {name}: {result['stdout'].split()[0]}")
        
        # Check environment variables
        required_env_vars = ["STARKNET_ACCOUNT", "STARKNET_KEYSTORE"]
        for var in required_env_vars:
            if not os.getenv(var):
                print(f"   ❌ Environment variable {var} not set")
                print(f"   💡 Set with: export {var}=path/to/your/{var.lower().replace('starknet_', '')}")
                return False
            else:
                path = os.getenv(var)
                if not Path(path).exists():
                    print(f"   ❌ {var} file not found: {path}")
                    return False
                print(f"   ✅ {var}: {path}")
        
        # Test network connectivity
        test_cmd = ["starkli", "chain-id", "--rpc", self.rpc_url]
        result = self.run_command(test_cmd, f"Testing {self.network} network connectivity")
        if not result["success"]:
            print(f"   ❌ Cannot connect to {self.network} network")
            return False
        else:
            print(f"   ✅ Network connectivity: Chain ID {result['stdout']}")
            
        return True
    
    def check_account_balance(self) -> bool:
        """Check if account has sufficient balance for deployment"""
        print("\n💰 Checking account balance...")
        
        balance_cmd = [
            "starkli", "balance", 
            "--rpc", self.rpc_url,
            "--account", os.getenv("STARKNET_ACCOUNT")
        ]
        
        result = self.run_command(balance_cmd, "Checking ETH balance")
        if not result["success"]:
            print("   ❌ Could not check balance")
            return False
            
        try:
            # Parse balance (format: "0.123456789 ETH")
            balance_line = result["stdout"].split('\n')[0]
            balance_eth = float(balance_line.split()[0])
            
            min_required = 0.01  # Minimum ETH required for deployment
            
            print(f"   💳 Current balance: {balance_eth} ETH")
            
            if balance_eth < min_required:
                print(f"   ❌ Insufficient balance. Need at least {min_required} ETH")
                print(f"   💡 Get testnet ETH from: https://faucet.goerli.starknet.io/")
                return False
            else:
                print(f"   ✅ Sufficient balance for deployment")
                return True
                
        except (IndexError, ValueError) as e:
            print(f"   ⚠️  Could not parse balance: {e}")
            print(f"   ⚠️  Continuing anyway...")
            return True
    
    def build_contracts(self) -> bool:
        """Build all contracts"""
        print("\n🔨 Building contracts...")
        
        result = self.run_command(["scarb", "build"], "Building Cairo contracts")
        if not result["success"]:
            print("❌ Contract build failed")
            return False
            
        # Verify contract artifacts exist
        for contract in self.contracts:
            contract_file = f"target/dev/astratrade_contracts_{contract['name']}.contract_class.json"
            if not Path(contract_file).exists():
                print(f"   ❌ Contract artifact missing: {contract_file}")
                return False
            else:
                print(f"   ✅ Built: {contract['name']}")
                
        return True
    
    def declare_contract(self, contract_name: str) -> Optional[str]:
        """Declare a contract and return class hash"""
        print(f"\n📝 Declaring {contract_name} contract...")
        
        contract_file = f"target/dev/astratrade_contracts_{contract_name}.contract_class.json"
        
        declare_cmd = [
            "starkli", "declare",
            contract_file,
            "--rpc", self.rpc_url,
            "--account", os.getenv("STARKNET_ACCOUNT"),
            "--keystore", os.getenv("STARKNET_KEYSTORE"),
            "--max-fee", "0.005"  # 0.005 ETH max fee
        ]
        
        result = self.run_command(declare_cmd, f"Declaring {contract_name}")
        
        if result["success"]:
            # Extract class hash from output
            lines = result["stdout"].split('\n')
            for line in lines:
                if "Class hash declared:" in line:
                    class_hash = line.split(":")[-1].strip()
                    print(f"   ✅ Class hash: {class_hash}")
                    return class_hash
                elif "already declared" in line.lower():
                    # Contract already declared, extract class hash
                    for line in lines:
                        if "0x" in line and len(line.strip()) == 66:
                            class_hash = line.strip()
                            print(f"   📋 Already declared: {class_hash}")
                            return class_hash
                            
        print(f"   ❌ Failed to declare {contract_name}")
        return None
    
    def deploy_contract(self, contract_info: Dict, deployed_addresses: Dict) -> Optional[Dict]:
        """Deploy a contract with constructor arguments"""
        contract_name = contract_info["name"]
        print(f"\n🚀 Deploying {contract_name} contract...")
        
        # Declare contract first
        class_hash = self.declare_contract(contract_name)
        if not class_hash:
            return None
            
        # Resolve constructor arguments
        constructor_args = []
        for arg in contract_info["constructor_args"]:
            if arg.startswith("${") and arg.endswith("}"):
                # Replace placeholder with deployed address
                placeholder = arg[2:-1]  # Remove ${ and }
                if placeholder in deployed_addresses:
                    constructor_args.append(deployed_addresses[placeholder])
                else:
                    print(f"   ❌ Dependency not found: {placeholder}")
                    return None
            else:
                constructor_args.append(arg)
                
        deploy_cmd = [
            "starkli", "deploy",
            class_hash,
            "--rpc", self.rpc_url,
            "--account", os.getenv("STARKNET_ACCOUNT"),
            "--keystore", os.getenv("STARKNET_KEYSTORE"),
            "--max-fee", "0.01"  # 0.01 ETH max fee
        ] + constructor_args
        
        result = self.run_command(deploy_cmd, f"Deploying {contract_name}", timeout=600)
        
        if result["success"]:
            # Parse deployment result
            lines = result["stdout"].split('\n')
            contract_address = None
            transaction_hash = None
            
            for line in lines:
                if "Contract deployed:" in line:
                    contract_address = line.split(":")[-1].strip()
                elif "Transaction hash:" in line:
                    transaction_hash = line.split(":")[-1].strip()
                    
            if contract_address and transaction_hash:
                deployment_info = {
                    "name": contract_name,
                    "class_name": contract_info["class_name"],
                    "description": contract_info["description"],
                    "address": contract_address,
                    "class_hash": class_hash,
                    "transaction_hash": transaction_hash,
                    "constructor_args": constructor_args,
                    "deployed_at": datetime.now().isoformat(),
                    "block_number": "pending"
                }
                
                print(f"   ✅ Deployed successfully!")
                print(f"   📍 Address: {contract_address}")
                print(f"   🧾 TX Hash: {transaction_hash}")
                
                return deployment_info
        
        print(f"   ❌ Failed to deploy {contract_name}")
        return None
    
    def wait_for_confirmations(self, deployment_info: Dict) -> bool:
        """Wait for transaction confirmation"""
        print(f"\n⏳ Waiting for confirmation: {deployment_info['name']}")
        
        tx_hash = deployment_info["transaction_hash"]
        max_attempts = 30  # 5 minutes with 10s intervals
        
        for attempt in range(max_attempts):
            receipt_cmd = [
                "starkli", "receipt",
                tx_hash,
                "--rpc", self.rpc_url
            ]
            
            result = self.run_command(receipt_cmd, f"Checking TX receipt (attempt {attempt + 1})")
            
            if result["success"]:
                # Parse receipt for block number
                lines = result["stdout"].split('\n')
                for line in lines:
                    if "Block number:" in line:
                        block_number = line.split(":")[-1].strip()
                        deployment_info["block_number"] = block_number
                        print(f"   ✅ Confirmed in block: {block_number}")
                        return True
                        
            print(f"   ⏳ Waiting... ({attempt + 1}/{max_attempts})")
            time.sleep(10)
            
        print(f"   ⚠️  Timeout waiting for confirmation")
        return False
    
    def deploy_all_contracts(self) -> bool:
        """Deploy all AstraTrade V2 contracts"""
        print("🚀 Starting AstraTrade V2 Contract Deployment")
        print("=" * 70)
        
        # Step 1: Prerequisites
        if not self.check_prerequisites():
            return False
            
        # Step 2: Account balance
        if not self.check_account_balance():
            return False
            
        # Step 3: Build contracts
        if not self.build_contracts():
            return False
            
        # Step 4: Deploy contracts in order
        deployed_addresses = {}
        deployment_success = True
        
        for contract_info in self.contracts:
            deployment_info = self.deploy_contract(contract_info, deployed_addresses)
            
            if not deployment_info:
                print(f"❌ Failed to deploy {contract_info['name']}")
                deployment_success = False
                break
                
            # Wait for confirmation
            self.wait_for_confirmations(deployment_info)
            
            # Store deployment info
            contract_name = contract_info["name"]
            self.deployment_data["contracts"][contract_name] = deployment_info
            self.deployment_data["deployment_order"].append(contract_name)
            
            # Add to deployed addresses for dependencies
            deployed_addresses[f"{contract_name}_address"] = deployment_info["address"]
            
        # Step 5: Save results
        self.save_deployment_results()
        
        return deployment_success
    
    def save_deployment_results(self):
        """Save deployment results with explorer links"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"astratrade_v2_deployment_{self.network}_{timestamp}.json"
        filepath = self.logs_dir / filename
        
        # Add explorer links and gas estimates
        for contract_name, contract_info in self.deployment_data["contracts"].items():
            address = contract_info["address"]
            tx_hash = contract_info["transaction_hash"]
            
            if self.network == "sepolia":
                contract_info["explorer_links"] = {
                    "starkscan": f"https://sepolia.starkscan.co/contract/{address}",
                    "voyager": f"https://sepolia.voyager.online/contract/{address}",
                    "transaction": f"https://sepolia.starkscan.co/tx/{tx_hash}"
                }
            elif self.network == "mainnet":
                contract_info["explorer_links"] = {
                    "starkscan": f"https://starkscan.co/contract/{address}",
                    "voyager": f"https://voyager.online/contract/{address}",
                    "transaction": f"https://starkscan.co/tx/{tx_hash}"
                }
        
        # Save deployment data
        with open(filepath, "w") as f:
            json.dump(self.deployment_data, f, indent=2)
            
        # Save as latest deployment
        latest_path = self.logs_dir / "latest_astratrade_v2_deployment.json"
        with open(latest_path, "w") as f:
            json.dump(self.deployment_data, f, indent=2)
            
        print(f"\n💾 Deployment results saved to: {filepath}")
        print(f"💾 Latest deployment: {latest_path}")
        
        # Print deployment summary
        self.print_deployment_summary()
        
        return filepath
    
    def print_deployment_summary(self):
        """Print formatted deployment summary"""
        print(f"\n{'='*70}")
        print(f"🎉 AstraTrade V2 Deployment Summary")
        print(f"{'='*70}")
        print(f"Network: {self.network}")
        print(f"RPC: {self.rpc_url}")
        print(f"Deployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Contracts: {len(self.deployment_data['contracts'])}")
        print()
        
        for contract_name in self.deployment_data["deployment_order"]:
            contract_info = self.deployment_data["contracts"][contract_name]
            print(f"📍 {contract_info['class_name']}:")
            print(f"   Address: {contract_info['address']}")
            print(f"   TX Hash: {contract_info['transaction_hash']}")
            print(f"   Block: {contract_info.get('block_number', 'pending')}")
            
            if "explorer_links" in contract_info:
                print(f"   Explorer: {contract_info['explorer_links']['starkscan']}")
            print()
        
        print("🔗 Integration Instructions:")
        print("1. Update Flutter services with deployed contract addresses")
        print("2. Run integration tests against deployed contracts")
        print("3. Update frontend configuration for Sepolia testnet")
        print(f"{'='*70}")


def main():
    """Main deployment function"""
    print("🚀 AstraTrade V2 Production Deployment Starting...")
    
    # Check if we're in the right directory
    if not Path("Scarb.toml").exists():
        print("❌ Please run this script from the project root directory")
        return False
        
    try:
        deployer = AstraTradeDeployer("sepolia")
        success = deployer.deploy_all_contracts()
        
        if success:
            print("\n🎉 All contracts deployed successfully!")
            print("Ready for production testing and bounty evaluation!")
        else:
            print("\n⚠️  Some deployments failed - check logs for details")
            
        return success
            
    except KeyboardInterrupt:
        print("\n⏹️  Deployment interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)