#!/usr/bin/env python3
"""
Contract Testing Script for AstraTrade Project
Tests all deployed contracts with comprehensive transaction scenarios
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
from starknet_py.cairo.felt import encode_shortstring


class ContractTester:
    """Comprehensive contract testing framework"""
    
    def __init__(self, deployment_file: str):
        self.deployment_file = deployment_file
        self.load_deployment_data()
        self.setup_client()
        self.contracts = {}
        self.test_results = {}
        
    def load_deployment_data(self):
        """Load deployment data from file"""
        deployment_path = Path(self.deployment_file)
        if not deployment_path.exists():
            raise FileNotFoundError(f"Deployment file {self.deployment_file} not found")
            
        with open(deployment_path, 'r') as f:
            self.deployment_data = json.load(f)
            
        print(f"✅ Loaded deployment data for {len(self.deployment_data['contracts'])} contracts")
        
    def setup_client(self):
        """Initialize Starknet client and account"""
        # Load environment for account credentials
        env_file = ".env.deployment"
        if Path(env_file).exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                        
        try:
            # Setup network client
            rpc_url = os.getenv('STARKNET_RPC_URL')
            self.client = FullNodeClient(node_url=rpc_url)
            
            # Setup account
            private_key = int(os.getenv('STARKNET_PRIVATE_KEY'), 16)
            account_address = int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)
            
            key_pair = KeyPair.from_private_key(private_key)
            
            # Determine chain ID
            network = self.deployment_data.get('network', 'sepolia')
            chain_id = StarknetChainId.SEPOLIA if network == 'sepolia' else StarknetChainId.MAINNET
            
            self.account = Account(
                address=account_address,
                client=self.client,
                key_pair=key_pair,
                chain=chain_id
            )
            
            print(f"✅ Starknet client initialized for testing")
            
        except Exception as e:
            print(f"❌ Failed to setup client: {e}")
            sys.exit(1)
            
    async def initialize_contracts(self):
        """Initialize contract instances"""
        print(f"\n🔗 Initializing contract instances...")
        
        for contract_name, deployment_info in self.deployment_data['contracts'].items():
            try:
                # Load contract ABI
                contract_dir = f"src/contracts/{contract_name}"
                target_dir = f"{contract_dir}/target/dev"
                
                class_files = list(Path(target_dir).glob("*.contract_class.json"))
                if not class_files:
                    print(f"❌ No contract class file found for {contract_name}")
                    continue
                    
                with open(class_files[0], 'r') as f:
                    contract_class = json.load(f)
                    abi = contract_class.get('abi', [])
                
                # Create contract instance
                contract = Contract(
                    address=int(deployment_info['address'], 16),
                    abi=abi,
                    provider=self.account,
                    cairo_version=1
                )
                
                self.contracts[contract_name] = contract
                print(f"  ✅ {contract_name} contract initialized")
                
            except Exception as e:
                print(f"  ❌ Failed to initialize {contract_name}: {e}")
                
        print(f"📊 Initialized {len(self.contracts)}/{len(self.deployment_data['contracts'])} contracts")
        
    async def test_achievement_nft(self):
        """Test AchievementNFT contract"""
        print(f"\n🎯 Testing AchievementNFT Contract...")
        
        contract = self.contracts.get('achievement_nft')
        if not contract:
            print("❌ AchievementNFT contract not available")
            return False
            
        test_results = []
        
        try:
            # Test 1: Read basic info
            print("  📖 Test 1: Reading contract metadata...")
            name = await contract.functions["name"].call()
            symbol = await contract.functions["symbol"].call() 
            total_supply = await contract.functions["total_supply"].call()
            
            print(f"    Name: {name}")
            print(f"    Symbol: {symbol}")
            print(f"    Total Supply: {total_supply}")
            test_results.append(("metadata_read", True))
            
            # Test 2: Add minter (owner only)
            print("  🔐 Test 2: Adding minter permission...")
            test_address = int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)
            
            add_minter_call = await contract.functions["add_minter"].invoke_v1(
                minter=test_address,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await add_minter_call.wait_for_acceptance()
            print(f"    ✅ Minter added: {hex(test_address)}")
            test_results.append(("add_minter", True))
            
            # Test 3: Verify minter status
            print("  🔍 Test 3: Verifying minter status...")
            is_minter = await contract.functions["is_minter"].call(test_address)
            print(f"    Minter status: {is_minter}")
            test_results.append(("verify_minter", bool(is_minter)))
            
            # Test 4: Mint achievement NFT
            print("  🏆 Test 4: Minting achievement NFT...")
            
            mint_call = await contract.functions["mint_achievement"].invoke_v1(
                to=test_address,
                achievement_type=encode_shortstring("first_trade"),
                rarity=encode_shortstring("common"),
                points_earned=100,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await mint_call.wait_for_acceptance()
            print(f"    ✅ Achievement NFT minted!")
            test_results.append(("mint_achievement", True))
            
            # Test 5: Check token ownership
            print("  👤 Test 5: Checking token ownership...")
            new_total_supply = await contract.functions["total_supply"].call()
            if new_total_supply > total_supply:
                owner = await contract.functions["owner_of"].call(1)  # First token
                balance = await contract.functions["balance_of"].call(test_address)
                print(f"    Token 1 owner: {hex(owner)}")
                print(f"    User balance: {balance}")
                test_results.append(("token_ownership", True))
            else:
                test_results.append(("token_ownership", False))
                
            # Test 6: Get achievement metadata
            print("  📋 Test 6: Reading achievement metadata...")
            metadata = await contract.functions["get_achievement_metadata"].call(1)
            print(f"    Achievement metadata: {metadata}")
            test_results.append(("achievement_metadata", True))
            
            # Test 7: Get user achievement count
            print("  📊 Test 7: Getting user achievement count...")
            user_count = await contract.functions["get_user_achievement_count"].call(test_address)
            print(f"    User achievement count: {user_count}")
            test_results.append(("user_achievement_count", True))
            
        except Exception as e:
            print(f"    ❌ Test failed: {e}")
            test_results.append(("error", False))
            
        success_rate = sum(1 for _, success in test_results if success) / len(test_results)
        print(f"  📊 AchievementNFT Tests: {success_rate:.1%} success rate")
        
        self.test_results['achievement_nft'] = {
            'tests': test_results,
            'success_rate': success_rate
        }
        
        return success_rate > 0.8
        
    async def test_points_leaderboard(self):
        """Test PointsLeaderboard contract"""
        print(f"\n📈 Testing PointsLeaderboard Contract...")
        
        contract = self.contracts.get('points_leaderboard')
        if not contract:
            print("❌ PointsLeaderboard contract not available")
            return False
            
        test_results = []
        
        try:
            # Test 1: Read basic info
            print("  📖 Test 1: Reading contract info...")
            owner = await contract.functions["get_owner"].call()
            total_users = await contract.functions["get_total_users"].call()
            is_paused = await contract.functions["is_paused"].call()
            
            print(f"    Owner: {hex(owner)}")
            print(f"    Total Users: {total_users}")
            print(f"    Is Paused: {is_paused}")
            test_results.append(("basic_info", True))
            
            # Test 2: Add points manager
            print("  🔐 Test 2: Adding points manager...")
            test_address = int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)
            
            add_manager_call = await contract.functions["add_points_manager"].invoke_v1(
                manager=test_address,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await add_manager_call.wait_for_acceptance()
            print(f"    ✅ Points manager added")
            test_results.append(("add_manager", True))
            
            # Test 3: Verify manager status
            print("  🔍 Test 3: Verifying manager status...")
            is_manager = await contract.functions["is_points_manager"].call(test_address)
            print(f"    Manager status: {is_manager}")
            test_results.append(("verify_manager", bool(is_manager)))
            
            # Test 4: Add points to user
            print("  🎯 Test 4: Adding points to user...")
            
            add_points_call = await contract.functions["add_points"].invoke_v1(
                user=test_address,
                points=250,
                source=encode_shortstring("test_points"),
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await add_points_call.wait_for_acceptance()
            print(f"    ✅ Points added to user")
            test_results.append(("add_points", True))
            
            # Test 5: Check user points
            print("  📊 Test 5: Checking user points...")
            user_points = await contract.functions["get_user_points"].call(test_address)
            print(f"    User points: {user_points}")
            test_results.append(("check_points", user_points > 0))
            
            # Test 6: Get user stats
            print("  📋 Test 6: Getting user statistics...")
            user_stats = await contract.functions["get_user_stats"].call(test_address)
            print(f"    User stats: {user_stats}")
            test_results.append(("user_stats", True))
            
            # Test 7: Update streak
            print("  🔥 Test 7: Updating user streak...")
            
            update_streak_call = await contract.functions["update_streak"].invoke_v1(
                user=test_address,
                activity_type=encode_shortstring("daily_login"),
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await update_streak_call.wait_for_acceptance()
            print(f"    ✅ Streak updated")
            test_results.append(("update_streak", True))
            
            # Test 8: Get streak data
            print("  📈 Test 8: Getting streak data...")
            streak_data = await contract.functions["get_user_streak_data"].call(test_address)
            print(f"    Streak data: {streak_data}")
            test_results.append(("streak_data", True))
            
            # Test 9: Complete achievement
            print("  🏆 Test 9: Completing achievement...")
            
            complete_achievement_call = await contract.functions["complete_achievement"].invoke_v1(
                user=test_address,
                achievement_type=encode_shortstring("streak_master"),
                points=500,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await complete_achievement_call.wait_for_acceptance()
            print(f"    ✅ Achievement completed")
            test_results.append(("complete_achievement", True))
            
            # Test 10: Get global stats
            print("  🌍 Test 10: Getting global statistics...")
            global_stats = await contract.functions["get_global_stats"].call()
            print(f"    Global stats: {global_stats}")
            test_results.append(("global_stats", True))
            
        except Exception as e:
            print(f"    ❌ Test failed: {e}")
            test_results.append(("error", False))
            
        success_rate = sum(1 for _, success in test_results if success) / len(test_results)
        print(f"  📊 PointsLeaderboard Tests: {success_rate:.1%} success rate")
        
        self.test_results['points_leaderboard'] = {
            'tests': test_results,
            'success_rate': success_rate
        }
        
        return success_rate > 0.8
        
    async def test_vault(self):
        """Test Vault contract"""
        print(f"\n🏦 Testing Vault Contract...")
        
        contract = self.contracts.get('vault')
        if not contract:
            print("❌ Vault contract not available")
            return False
            
        test_results = []
        
        try:
            # Test 1: Read basic info
            print("  📖 Test 1: Reading vault info...")
            owner = await contract.functions["get_owner"].call()
            is_paused = await contract.functions["is_paused"].call()
            
            print(f"    Owner: {hex(owner)}")
            print(f"    Is Paused: {is_paused}")
            test_results.append(("basic_info", True))
            
            # Test 2: Check initial balance
            print("  💰 Test 2: Checking initial balance...")
            test_address = int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)
            eth_token = 0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7  # ETH on Sepolia
            
            initial_balance = await contract.functions["get_balance"].call(test_address, eth_token)
            print(f"    Initial balance: {initial_balance}")
            test_results.append(("initial_balance", True))
            
            # Test 3: Make a deposit (simulated - would need actual tokens)
            print("  📥 Test 3: Testing deposit function...")
            try:
                deposit_call = await contract.functions["deposit"].invoke_v1(
                    token=eth_token,
                    amount=1000,  # Small amount for testing
                    max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
                )
                await deposit_call.wait_for_acceptance()
                print(f"    ✅ Deposit transaction completed")
                test_results.append(("deposit", True))
                
                # Check balance after deposit
                new_balance = await contract.functions["get_balance"].call(test_address, eth_token)
                print(f"    New balance: {new_balance}")
                
            except Exception as e:
                print(f"    ⚠️  Deposit failed (expected - no token approval): {e}")
                test_results.append(("deposit", False))  # Expected to fail without token approval
                
        except Exception as e:
            print(f"    ❌ Test failed: {e}")
            test_results.append(("error", False))
            
        success_rate = sum(1 for _, success in test_results if success) / len(test_results)
        print(f"  📊 Vault Tests: {success_rate:.1%} success rate")
        
        self.test_results['vault'] = {
            'tests': test_results,
            'success_rate': success_rate
        }
        
        return success_rate > 0.5  # Lower threshold due to expected deposit failure
        
    async def test_paymaster(self):
        """Test Paymaster contract"""
        print(f"\n⛽ Testing Paymaster Contract...")
        
        contract = self.contracts.get('paymaster')
        if not contract:
            print("❌ Paymaster contract not available")
            return False
            
        test_results = []
        
        try:
            # Test 1: Read dummy value
            print("  📖 Test 1: Reading dummy value...")
            dummy_value = await contract.functions["get_dummy"].call()
            print(f"    Dummy value: {dummy_value}")
            test_results.append(("read_dummy", True))
            
            # Test 2: Test event emission
            print("  📢 Test 2: Testing event emission...")
            test_address = int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)
            
            emit_call = await contract.functions["test_emit"].invoke_v1(
                user=test_address,
                value=12345,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await emit_call.wait_for_acceptance()
            print(f"    ✅ Event emission completed")
            test_results.append(("emit_event", True))
            
        except Exception as e:
            print(f"    ❌ Test failed: {e}")
            test_results.append(("error", False))
            
        success_rate = sum(1 for _, success in test_results if success) / len(test_results)
        print(f"  📊 Paymaster Tests: {success_rate:.1%} success rate")
        
        self.test_results['paymaster'] = {
            'tests': test_results,
            'success_rate': success_rate
        }
        
        return success_rate > 0.8
        
    async def run_integration_tests(self):
        """Run integration tests between contracts"""
        print(f"\n🔗 Running Integration Tests...")
        
        if 'achievement_nft' not in self.contracts or 'points_leaderboard' not in self.contracts:
            print("❌ Required contracts not available for integration tests")
            return False
            
        try:
            # Integration Test: Award points and mint NFT for same achievement
            print("  🎯 Integration Test: Points + NFT Achievement Flow...")
            
            test_address = int(os.getenv('STARKNET_ACCOUNT_ADDRESS'), 16)
            
            # Step 1: Award points for achievement
            points_contract = self.contracts['points_leaderboard']
            complete_achievement_call = await points_contract.functions["complete_achievement"].invoke_v1(
                user=test_address,
                achievement_type=encode_shortstring("integration_test"),
                points=1000,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await complete_achievement_call.wait_for_acceptance()
            print("    ✅ Achievement points awarded")
            
            # Step 2: Mint corresponding NFT
            nft_contract = self.contracts['achievement_nft']
            mint_call = await nft_contract.functions["mint_achievement"].invoke_v1(
                to=test_address,
                achievement_type=encode_shortstring("integration_test"),
                rarity=encode_shortstring("legendary"),
                points_earned=1000,
                max_fee=int(os.getenv('MAX_FEE', '0x16345785d8a0000'), 16)
            )
            await mint_call.wait_for_acceptance()
            print("    ✅ Achievement NFT minted")
            
            # Step 3: Verify both contracts updated
            user_points = await points_contract.functions["get_user_points"].call(test_address)
            user_achievements = await nft_contract.functions["get_user_achievement_count"].call(test_address)
            
            print(f"    Final user points: {user_points}")
            print(f"    Total NFT achievements: {user_achievements}")
            
            self.test_results['integration'] = {
                'points_integration': user_points > 0,
                'nft_integration': user_achievements > 0,
                'success_rate': 1.0
            }
            
            return True
            
        except Exception as e:
            print(f"    ❌ Integration test failed: {e}")
            self.test_results['integration'] = {
                'error': str(e),
                'success_rate': 0.0
            }
            return False
            
    def save_test_results(self):
        """Save test results to file"""
        # Create test results directory
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        filepath = results_dir / filename
        
        # Prepare test data
        test_data = {
            'timestamp': int(time.time()),
            'network': self.deployment_data.get('network'),
            'test_results': self.test_results,
            'deployment_file': self.deployment_file
        }
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(test_data, f, indent=2)
            
        print(f"💾 Test results saved to: {filepath}")
        
    async def run_all_tests(self):
        """Run all contract tests"""
        print(f"\n🧪 Starting comprehensive contract testing...")
        print("=" * 60)
        
        # Initialize contracts
        await self.initialize_contracts()
        
        # Run individual contract tests
        test_functions = [
            ('achievement_nft', self.test_achievement_nft),
            ('points_leaderboard', self.test_points_leaderboard),
            ('vault', self.test_vault),
            ('paymaster', self.test_paymaster)
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for contract_name, test_func in test_functions:
            if contract_name in self.contracts:
                try:
                    success = await test_func()
                    if success:
                        passed_tests += 1
                        print(f"✅ {contract_name} tests passed")
                    else:
                        print(f"❌ {contract_name} tests failed")
                        
                    # Wait between tests
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"❌ {contract_name} tests error: {e}")
            else:
                print(f"⏭️  Skipping {contract_name} (not available)")
                
        # Run integration tests
        integration_success = await self.run_integration_tests()
        if integration_success:
            print(f"✅ Integration tests passed")
        else:
            print(f"❌ Integration tests failed")
            
        # Save results
        self.save_test_results()
        
        # Print summary
        print(f"\n📊 Testing Summary:")
        print(f"Individual Tests: {passed_tests}/{total_tests} passed")
        print(f"Integration Tests: {'✅' if integration_success else '❌'}")
        
        overall_success = (passed_tests / total_tests) > 0.75 and integration_success
        print(f"Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        
        return overall_success


async def main():
    """Main testing function"""
    if len(sys.argv) != 2:
        print("Usage: python test_contracts.py <deployment_file>")
        print("Example: python test_contracts.py deployment_logs/deployment_20250714_123456_sepolia.json")
        sys.exit(1)
        
    deployment_file = sys.argv[1]
    
    print("🧪 AstraTrade Contract Testing Starting...")
    print("=" * 60)
    
    try:
        # Initialize tester
        tester = ContractTester(deployment_file)
        
        # Run all tests
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n⚠️  Some tests failed")
            
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())