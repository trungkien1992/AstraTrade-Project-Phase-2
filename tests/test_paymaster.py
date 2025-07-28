#!/usr/bin/env python3
"""
AstraTrade Paymaster Contract Tests
Comprehensive testing for gasless transaction functionality
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.cairo.felt import encode_shortstring

class PaymasterTester:
    def __init__(self, network: str = "sepolia"):
        """Initialize paymaster testing environment."""
        self.network = network
        self.client = None
        self.account = None
        self.paymaster_contract = None
        self.test_results = []
        
    async def setup(self):
        """Set up test environment and contracts."""
        print(f"🔧 Setting up paymaster test environment on {self.network}...")
        
        # Initialize client
        if self.network == "sepolia":
            self.client = GatewayClient("https://free-rpc.nethermind.io/sepolia-juno")
            chain_id = StarknetChainId.SEPOLIA
        else:
            raise ValueError(f"Unsupported network: {self.network}")
        
        # Load environment variables
        private_key = os.getenv("STARKNET_PRIVATE_KEY")
        account_address = os.getenv("STARKNET_ACCOUNT_ADDRESS")
        
        if not private_key or not account_address:
            print("❌ Missing STARKNET_PRIVATE_KEY or STARKNET_ACCOUNT_ADDRESS environment variables")
            return False
        
        # Create account
        key_pair = KeyPair.from_private_key(int(private_key, 16))
        self.account = Account(
            address=account_address,
            client=self.client,
            chain=chain_id,
            key_pair=key_pair
        )
        
        print("✅ Test environment setup complete")
        return True
    
    async def run_test(self, test_name: str, test_func):
        """Run individual test and track results."""
        try:
            print(f"🧪 Running test: {test_name}")
            result = await test_func()
            self.test_results.append([test_name, result])
            status = "✅" if result else "❌"
            print(f"{status} {test_name}: {'PASSED' if result else 'FAILED'}")
            return result
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {str(e)}")
            self.test_results.append([test_name, False])
            return False
    
    async def test_paymaster_deployment(self) -> bool:
        """Test that paymaster can be deployed successfully."""
        try:
            # Load paymaster contract class
            contract_class_path = project_root / "target" / "dev" / "astratrade_AstraTradePaymaster.contract_class.json"
            
            if not contract_class_path.exists():
                print("⚠️  Paymaster contract not compiled. Compiling now...")
                compile_result = os.system("cd " + str(project_root) + " && scarb build")
                if compile_result != 0:
                    return False
            
            if contract_class_path.exists():
                with open(contract_class_path, 'r') as f:
                    contract_class = json.load(f)
                
                # Deploy paymaster with test parameters
                daily_limit = 1000000000000000000  # 1 ETH
                per_tx_limit = 100000000000000000   # 0.1 ETH
                min_balance = 10000000000000000     # 0.01 ETH
                
                deployment = await Contract.deploy_v1(
                    account=self.account,
                    class_hash=None,  # Will be calculated
                    abi=contract_class["abi"],
                    bytecode=contract_class["sierra_program"],
                    constructor_args=[
                        self.account.address,  # owner
                        daily_limit,
                        per_tx_limit,
                        min_balance
                    ]
                )
                
                await deployment.wait_for_acceptance()
                self.paymaster_contract = deployment.deployed_contract
                print(f"📍 Paymaster deployed at: {hex(self.paymaster_contract.address)}")
                return True
            
            return False
        except Exception as e:
            print(f"Deployment error: {e}")
            return False
    
    async def test_paymaster_initialization(self) -> bool:
        """Test paymaster initial state."""
        if not self.paymaster_contract:
            return False
        
        try:
            # Check owner
            owner = await self.paymaster_contract.functions["get_owner"].call()
            if owner.owner != self.account.address:
                return False
            
            # Check initial balance
            balance = await self.paymaster_contract.functions["get_balance"].call()
            if balance.balance != 0:
                return False
            
            return True
        except Exception as e:
            print(f"Initialization test error: {e}")
            return False
    
    async def test_whitelist_management(self) -> bool:
        """Test user whitelisting functionality."""
        if not self.paymaster_contract:
            return False
        
        try:
            test_user = 0x123456789
            
            # Initially not whitelisted
            is_whitelisted = await self.paymaster_contract.functions["is_whitelisted"].call(test_user)
            if is_whitelisted.result:
                return False
            
            # Add to whitelist
            invoke = await self.paymaster_contract.functions["add_whitelisted_user"].invoke_v1(
                test_user,
                max_fee=int(1e16)
            )
            await invoke.wait_for_acceptance()
            
            # Check whitelisted
            is_whitelisted = await self.paymaster_contract.functions["is_whitelisted"].call(test_user)
            if not is_whitelisted.result:
                return False
            
            # Remove from whitelist
            invoke = await self.paymaster_contract.functions["remove_whitelisted_user"].invoke_v1(
                test_user,
                max_fee=int(1e16)
            )
            await invoke.wait_for_acceptance()
            
            # Check not whitelisted
            is_whitelisted = await self.paymaster_contract.functions["is_whitelisted"].call(test_user)
            if is_whitelisted.result:
                return False
            
            return True
        except Exception as e:
            print(f"Whitelist test error: {e}")
            return False
    
    async def test_balance_management(self) -> bool:
        """Test paymaster balance deposit/withdraw."""
        if not self.paymaster_contract:
            return False
        
        try:
            # Check initial balance
            initial_balance = await self.paymaster_contract.functions["get_balance"].call()
            
            # Deposit funds (mock for testing)
            invoke = await self.paymaster_contract.functions["deposit"].invoke_v1(
                max_fee=int(1e16)
            )
            await invoke.wait_for_acceptance()
            
            # Check balance increased
            new_balance = await self.paymaster_contract.functions["get_balance"].call()
            if new_balance.balance <= initial_balance.balance:
                return False
            
            return True
        except Exception as e:
            print(f"Balance test error: {e}")
            return False
    
    async def test_configuration_management(self) -> bool:
        """Test paymaster configuration updates."""
        if not self.paymaster_contract:
            return False
        
        try:
            # Set new daily limit
            new_limit = 2000000000000000000  # 2 ETH
            invoke = await self.paymaster_contract.functions["set_daily_limit"].invoke_v1(
                new_limit,
                max_fee=int(1e16)
            )
            await invoke.wait_for_acceptance()
            
            # Set new per-tx limit
            new_per_tx = 200000000000000000  # 0.2 ETH
            invoke = await self.paymaster_contract.functions["set_per_tx_limit"].invoke_v1(
                new_per_tx,
                max_fee=int(1e16)
            )
            await invoke.wait_for_acceptance()
            
            return True
        except Exception as e:
            print(f"Configuration test error: {e}")
            return False
    
    async def test_emergency_controls(self) -> bool:
        """Test pause and emergency stop functionality."""
        if not self.paymaster_contract:
            return False
        
        try:
            # Test pause
            invoke = await self.paymaster_contract.functions["pause"].invoke_v1(
                max_fee=int(1e16)
            )
            await invoke.wait_for_acceptance()
            
            # Test unpause
            invoke = await self.paymaster_contract.functions["unpause"].invoke_v1(
                max_fee=int(1e16)
            )
            await invoke.wait_for_acceptance()
            
            return True
        except Exception as e:
            print(f"Emergency controls test error: {e}")
            return False
    
    async def test_usage_tracking(self) -> bool:
        """Test gas usage tracking functionality."""
        if not self.paymaster_contract:
            return False
        
        try:
            # Get initial stats
            stats = await self.paymaster_contract.functions["get_sponsored_stats"].call()
            initial_count = stats.result[0]
            initial_gas = stats.result[1]
            
            # Check user daily usage (should be 0 initially)
            usage = await self.paymaster_contract.functions["get_user_daily_usage"].call(
                self.account.address
            )
            if usage.result != 0:
                return False
            
            return True
        except Exception as e:
            print(f"Usage tracking test error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run complete paymaster test suite."""
        print("🧪 Starting AstraTrade Paymaster Test Suite")
        print("=" * 50)
        
        if not await self.setup():
            print("❌ Test setup failed")
            return
        
        # Run all tests
        await self.run_test("Paymaster Deployment", self.test_paymaster_deployment)
        await self.run_test("Paymaster Initialization", self.test_paymaster_initialization)
        await self.run_test("Whitelist Management", self.test_whitelist_management)
        await self.run_test("Balance Management", self.test_balance_management)
        await self.run_test("Configuration Management", self.test_configuration_management)
        await self.run_test("Emergency Controls", self.test_emergency_controls)
        await self.run_test("Usage Tracking", self.test_usage_tracking)
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, result in self.test_results if result)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print(f"📊 Paymaster Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1%}")
        
        if success_rate == 1.0:
            print("🎉 All paymaster tests passed!")
        elif success_rate >= 0.8:
            print("✅ Most paymaster tests passed")
        else:
            print("❌ Significant paymaster test failures")
        
        return {
            "paymaster_tests": {
                "tests": self.test_results,
                "success_rate": success_rate,
                "total_tests": total_tests,
                "passed_tests": passed_tests
            }
        }

async def main():
    """Main test execution."""
    tester = PaymasterTester("sepolia")
    results = await tester.run_all_tests()
    
    # Save results
    if results:
        results_dir = project_root / "test_results"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = asyncio.get_event_loop().time()
        results_file = results_dir / f"paymaster_test_results_{int(timestamp)}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Test results saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(main())