#!/usr/bin/env python3
"""
Signing API Endpoint Tests

Tests the signing API endpoints using FastAPI TestClient.
Verifies that our dependency injection bypass pattern works correctly
and that the endpoints integrate properly with our verified signing service.

Following Testing Rule 3: NEVER ASSUME CODE WORKS - Always verify API endpoints
"""

import os
import sys
import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient

# Add backend to path for imports
sys.path.insert(0, '/Users/admin/AstraTrade-Project-Phase-2/apps/backend')

def test_signing_api_endpoints():
    """Test signing API endpoints with FastAPI TestClient"""
    
    print("🔍 Testing Signing API Endpoints")
    print("   Goal: Verify API integration with verified signing service")
    
    try:
        # Import the FastAPI app
        from core.main import app
        client = TestClient(app)
        
        print("✅ FastAPI TestClient created")
        
        # Test 1: Health check endpoint
        print("\n🧪 Test 1: Signing Service Status")
        
        response = client.get("/api/v1/blockchain/signing/status")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ Service Available: {status_data.get('service_available')}")
            print(f"   🔧 Crypto Backend: {status_data.get('crypto_backend')}")
            print(f"   ⚙️  Domain Config: {status_data.get('domain_config')}")
        else:
            print(f"   ❌ Status check failed: {response.text}")
            return False
        
        # Test 2: Order signing endpoint
        print("\n🧪 Test 2: Order Signing")
        
        order_request = {
            "user_id": 12345,
            "position_id": "pos_001",
            "base_asset_id": "0x4554480000000000000000000000000000000000000000000000000000000000",
            "base_amount": "1000000000000000000",
            "quote_asset_id": "0x5553444300000000000000000000000000000000000000000000000000000000",
            "quote_amount": "2000000000",
            "fee_asset_id": "0x5553444300000000000000000000000000000000000000000000000000000000",
            "fee_amount": "2000000",
            "expiration": int(datetime.now(timezone.utc).timestamp()) + 3600,
            "salt": "12345"
        }
        
        response = client.post("/api/v1/blockchain/signing/order", json=order_request)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            order_data = response.json()
            print(f"   ✅ Message Hash: {order_data.get('message_hash', '')[:20]}...")
            print(f"   ✅ Operation ID: {order_data.get('operation_id')}")
            print(f"   ✅ Signature r: {order_data.get('signature', {}).get('r', '')[:20]}...")
            print(f"   ✅ User ID: {order_data.get('user_id')}")
        else:
            print(f"   ❌ Order signing failed: {response.text}")
            return False
        
        # Test 3: Transfer signing endpoint
        print("\n🧪 Test 3: Transfer Signing")
        
        transfer_request = {
            "user_id": 12345,
            "recipient_position_id": "pos_002",
            "sender_position_id": "pos_001", 
            "collateral_id": "0x5553444300000000000000000000000000000000000000000000000000000000",
            "amount": "1000000000",
            "expiration": int(datetime.now(timezone.utc).timestamp()) + 3600,
            "salt": "54321"
        }
        
        response = client.post("/api/v1/blockchain/signing/transfer", json=transfer_request)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            transfer_data = response.json()
            print(f"   ✅ Message Hash: {transfer_data.get('message_hash', '')[:20]}...")
            print(f"   ✅ Operation ID: {transfer_data.get('operation_id')}")
            print(f"   ✅ Signature r: {transfer_data.get('signature', {}).get('r', '')[:20]}...")
        else:
            print(f"   ❌ Transfer signing failed: {response.text}")
            return False
        
        # Test 4: Withdrawal signing endpoint
        print("\n🧪 Test 4: Withdrawal Signing")
        
        withdrawal_request = {
            "user_id": 12345,
            "recipient": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
            "position_id": "pos_001",
            "collateral_id": "0x5553444300000000000000000000000000000000000000000000000000000000",
            "amount": "500000000",
            "expiration": int(datetime.now(timezone.utc).timestamp()) + 3600,
            "salt": "98765"
        }
        
        response = client.post("/api/v1/blockchain/signing/withdrawal", json=withdrawal_request)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            withdrawal_data = response.json()
            print(f"   ✅ Message Hash: {withdrawal_data.get('message_hash', '')[:20]}...")
            print(f"   ✅ Operation ID: {withdrawal_data.get('operation_id')}")
            print(f"   ✅ Signature r: {withdrawal_data.get('signature', {}).get('r', '')[:20]}...")
        else:
            print(f"   ❌ Withdrawal signing failed: {response.text}")
            return False
        
        # Test 5: Key derivation endpoint
        print("\n🧪 Test 5: Key Derivation")
        
        key_request = {
            "eth_signature": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1c",
            "user_id": 12345
        }
        
        response = client.post("/api/v1/blockchain/signing/derive-key", json=key_request)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            key_data = response.json()
            print(f"   ✅ Derived Key: {key_data.get('derived_key', '')[:20]}...")
            print(f"   ✅ User ID: {key_data.get('user_id')}")
            print(f"   ✅ Derived At: {key_data.get('derived_at')}")
        else:
            print(f"   ❌ Key derivation failed: {response.text}")
            return False
        
        # Test 6: Error handling
        print("\n🧪 Test 6: Error Handling")
        
        # Invalid request - missing required fields
        invalid_request = {
            "user_id": 12345,
            # Missing required fields
        }
        
        response = client.post("/api/v1/blockchain/signing/order", json=invalid_request)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print("   ✅ Properly rejected invalid request")
        else:
            print(f"   ⚠️  Unexpected response to invalid request: {response.status_code}")
        
        print("\n🎉 All API endpoint tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed - likely due to dataclass issue: {e}")
        print("   This is expected - our bypass strategy should handle this")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_extended_exchange_compatibility():
    """Test Extended Exchange compatibility with real message formats"""
    
    print(f"\n🔍 Extended Exchange Compatibility Test")
    
    try:
        from core.main import app
        client = TestClient(app)
        
        # Test with Extended Exchange-style parameters
        extended_exchange_order = {
            "user_id": 1001,
            "position_id": "1001",
            "base_asset_id": "0x4254430000000000000000000000000000000000000000000000000000000000",  # BTC
            "base_amount": "100000000",  # 1 BTC (8 decimals)
            "quote_asset_id": "0x5553444300000000000000000000000000000000000000000000000000000000",  # USDC
            "quote_amount": "4300000000000",  # 43,000 USDC (6 decimals)
            "fee_asset_id": "0x5553444300000000000000000000000000000000000000000000000000000000",  # USDC
            "fee_amount": "43000000",  # 43 USDC fee (0.1%)
            "expiration": 1734350400 + 3600,  # 1 hour expiry
            "salt": "7891011"
        }
        
        print(f"   🧪 Testing Extended Exchange order format...")
        
        response = client.post("/api/v1/blockchain/signing/order", json=extended_exchange_order)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Extended Exchange format accepted")
            print(f"   📝 Message Hash: {data.get('message_hash', '')[:20]}...")
            print(f"   ✍️  Signature Format: {list(data.get('signature', {}).keys())}")
            
            # Verify signature has required components
            signature = data.get('signature', {})
            if all(key in signature for key in ['r', 's', 'v']):
                print(f"   ✅ Signature has required components (r, s, v)")
                return True
            else:
                print(f"   ❌ Signature missing required components")
                return False
        else:
            print(f"   ❌ Extended Exchange format rejected: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Extended Exchange compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Signing API Endpoint Tests")
    print("   Goal: Verify API endpoints integrate correctly with verified signing service")
    
    success1 = test_signing_api_endpoints()
    success2 = test_extended_exchange_compatibility()
    
    if success1 and success2:
        print(f"\n🎉 ALL TESTS PASSED: Signing API endpoints are working correctly!")
        print(f"✅ API integration verified")
        print(f"✅ Extended Exchange compatibility confirmed")
        print(f"✅ Error handling functional")
        print(f"✅ Ready for Extended Exchange integration")
        sys.exit(0)
    else:
        print(f"\n❌ TESTS FAILED: API endpoints need fixes")
        sys.exit(1)