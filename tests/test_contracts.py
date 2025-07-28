#!/usr/bin/env python3
"""
Contract Testing Script for AstraTrace Project
Tests AchievementNFT and PointsLeaderboard contracts
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

def test_contract_compilation():
    """Test contract compilation"""
    print("=" * 80)
    print("🏗️  CONTRACT COMPILATION TESTS")
    print("=" * 80)
    
    contracts = [
        ("AchievementNFT", "src/contracts/achievement_nft"),
        ("PointsLeaderboard", "src/contracts/points_leaderboard"),
        ("Vault", "src/contracts/vault"),
        ("Paymaster", "src/contracts/paymaster")
    ]
    
    results = []
    
    for name, path in contracts:
        success = run_command(
            f"cd {path} && scarb build", 
            f"Building {name} contract"
        )
        results.append((name, success))
    
    return results

def check_contract_artifacts():
    """Check if contract artifacts were generated"""
    print("\n=" * 80)
    print("📁 CONTRACT ARTIFACTS CHECK")
    print("=" * 80)
    
    artifact_paths = [
        "src/contracts/achievement_nft/target",
        "src/contracts/points_leaderboard/target", 
        "src/contracts/vault/target",
        "src/contracts/paymaster/target"
    ]
    
    for path in artifact_paths:
        full_path = Path("/Users/admin/AstraTrade-Project") / path
        if full_path.exists():
            print(f"✅ {path} - artifacts found")
            # List contents
            try:
                for item in full_path.rglob("*"):
                    if item.is_file():
                        print(f"   📄 {item.relative_to(full_path)}")
            except Exception as e:
                print(f"   ⚠️  Error listing files: {e}")
        else:
            print(f"❌ {path} - no artifacts found")

def validate_contract_interfaces():
    """Validate contract interfaces and ABIs"""
    print("\n=" * 80)
    print("🔧 CONTRACT INTERFACE VALIDATION")
    print("=" * 80)
    
    # Check for contract ABIs in target directories
    contracts = ["achievement_nft", "points_leaderboard", "vault", "paymaster"]
    
    for contract in contracts:
        abi_path = f"src/contracts/{contract}/target/dev/{contract}.contract_class.json"
        full_path = Path("/Users/admin/AstraTrade-Project") / abi_path
        
        if full_path.exists():
            print(f"✅ {contract} - ABI found")
            try:
                with open(full_path, 'r') as f:
                    abi_data = json.load(f)
                    if 'abi' in abi_data:
                        abi_entries = len(abi_data['abi'])
                        print(f"   📊 ABI has {abi_entries} entries")
                    else:
                        print("   ⚠️  No ABI section found")
            except Exception as e:
                print(f"   ❌ Error reading ABI: {e}")
        else:
            print(f"❌ {contract} - ABI not found at {abi_path}")

def run_syntax_validation():
    """Run Cairo syntax validation"""
    print("\n=" * 80)
    print("✏️  CAIRO SYNTAX VALIDATION")
    print("=" * 80)
    
    cairo_files = [
        "src/contracts/achievement_nft/src/lib.cairo",
        "src/contracts/points_leaderboard/src/lib.cairo",
        "src/contracts/vault/src/lib.cairo", 
        "src/contracts/paymaster/src/lib.cairo"
    ]
    
    for cairo_file in cairo_files:
        success = run_command(
            f"scarb check --manifest-path {cairo_file.replace('/src/lib.cairo', '/Scarb.toml')}",
            f"Syntax check for {cairo_file}"
        )

def display_contract_summary():
    """Display summary of contract features"""
    print("\n=" * 80)
    print("📋 CONTRACT FEATURE SUMMARY")
    print("=" * 80)
    
    contracts_info = {
        "AchievementNFT": {
            "type": "ERC721 NFT Contract",
            "features": [
                "Achievement minting with metadata",
                "Role-based access control (owner, minters)",
                "Achievement tracking with rarity and points",
                "Standard ERC721 functionality",
                "Event emission for all major actions"
            ]
        },
        "PointsLeaderboard": {
            "type": "Leaderboard & Points System",
            "features": [
                "User points tracking and management", 
                "Daily/weekly streak calculations",
                "Global statistics aggregation",
                "Achievement completion tracking",
                "Role-based points management",
                "Leaderboard ranking system"
            ]
        },
        "Vault": {
            "type": "Token Vault Contract",
            "features": [
                "Multi-token deposit system",
                "User balance tracking",
                "Owner controls and pausing",
                "Event emission for deposits"
            ]
        },
        "Paymaster": {
            "type": "Gas Fee Management",
            "features": [
                "Simple test contract",
                "Event emission capability",
                "Basic state management"
            ]
        }
    }
    
    for name, info in contracts_info.items():
        print(f"\n🔹 {name} ({info['type']})")
        for feature in info['features']:
            print(f"   • {feature}")

def main():
    """Main test execution"""
    print("🚀 STARTING CONTRACT TESTS FOR ASTRATRADE PROJECT")
    print("=" * 80)
    
    # Run compilation tests
    compilation_results = test_contract_compilation()
    
    # Check artifacts
    check_contract_artifacts()
    
    # Validate interfaces
    validate_contract_interfaces()
    
    # Syntax validation
    run_syntax_validation()
    
    # Display summary
    display_contract_summary()
    
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
        print(f"\n⚠️  {total - passed} contracts failed compilation")
        return 1

if __name__ == "__main__":
    sys.exit(main())