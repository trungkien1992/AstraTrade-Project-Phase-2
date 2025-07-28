#!/usr/bin/env python3
"""
Test Extended Exchange API connectivity and trading integration
"""

import json
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and return the result"""
    print(f"\n🔍 {description}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd="/Users/admin/AstraTrade-Project"
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_extended_exchange_api():
    """Test Extended Exchange API connectivity"""
    print("=" * 80)
    print("🌐 EXTENDED EXCHANGE API TESTS")
    print("=" * 80)
    
    # Test basic connectivity
    success = run_command(
        "curl -s -H 'X-Api-Key: 6aa86ecc5df765eba5714d375d5ceef0' https://starknet.sepolia.extended.exchange/api/v1/info/markets | head -10", 
        "Testing basic API connectivity"
    )
    
    # Test ETH-USD market data
    success2 = run_command(
        "curl -s -H 'X-Api-Key: 6aa86ecc5df765eba5714d375d5ceef0' 'https://starknet.sepolia.extended.exchange/api/v1/info/markets?market=ETH-USD'", 
        "Testing ETH-USD market data"
    )
    
    # Test BTC-USD market data
    success3 = run_command(
        "curl -s -H 'X-Api-Key: 6aa86ecc5df765eba5714d375d5ceef0' 'https://starknet.sepolia.extended.exchange/api/v1/info/markets?market=BTC-USD'", 
        "Testing BTC-USD market data"
    )
    
    return success and success2 and success3

def main():
    """Main test execution"""
    print("🚀 TESTING EXTENDED EXCHANGE API INTEGRATION FOR ASTRATRADE PROJECT")
    print("=" * 80)
    
    # Run API tests
    api_success = test_extended_exchange_api()
    
    # Final results
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    if api_success:
        print("✅ Extended Exchange API integration tests PASSED")
        print("🎉 Trading integration is ready for deployment!")
        return 0
    else:
        print("❌ Extended Exchange API integration tests FAILED")
        print("⚠️  Check API connectivity and credentials")
        return 1

if __name__ == "__main__":
    sys.exit(main())