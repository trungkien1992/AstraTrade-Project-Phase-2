#!/usr/bin/env python3
"""
Simple test script to verify contract compilation
"""

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

def test_contract_compilation():
    """Test contract compilation"""
    print("=" * 80)
    print("🏗️  CONTRACT COMPILATION TESTS")
    print("=" * 80)
    
    # Test all contracts together
    success = run_command(
        "cd apps/contracts && scarb build", 
        "Building all contracts"
    )
    
    return [("All Contracts", success)]

def main():
    """Main test execution"""
    print("🚀 TESTING CONTRACT COMPILATION FOR ASTRATRADE PROJECT")
    print("=" * 80)
    
    # Run compilation tests
    compilation_results = test_contract_compilation()
    
    # Final results
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for _, success in compilation_results if success)
    total = len(compilation_results)
    
    print(f"Compilation Tests: {passed}/{total} passed")
    
    for name, success in compilation_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name}: {status}")
    
    if passed == total:
        print(f"\n🎉 ALL CONTRACTS COMPILED SUCCESSFULLY!")
        return 0
    else:
        print(f"\n⚠️  Contract compilation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())