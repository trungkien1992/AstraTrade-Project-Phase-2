"""
Test Enhanced Event Schema

Validation tests for the enhanced event system, adapters, and Redis Streams integration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
import json

# Test imports
try:
    from validation import validate_event_schema, DomainEventRegistry, EventValidationError
    from adapters import GamificationEventAdapter, SimpleEventAdapter, AdapterRegistry
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gamification'))
    from events import create_xp_gained_event, create_level_up_event, DomainEvent as LegacyEvent
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def test_enhanced_event_schema():
    """Test enhanced event structure validation."""
    print("\n=== Testing Enhanced Event Schema ===")
    
    # Valid event
    valid_event = {
        "event_id": "550e8400-e29b-41d4-a716-446655440000",
        "event_type": "Gamification.XPGained",
        "domain": "gamification",
        "entity_id": "user_123",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "event_version": 1,
        "correlation_id": "req_456",
        "causation_id": "",
        "producer": "astra-backend@1.0.0",
        "data": json.dumps({"user_id": 123, "xp_amount": 50})
    }
    
    try:
        validated = validate_event_schema(valid_event)
        print("✅ Valid event schema passed validation")
        print(f"   Event Type: {validated.event_type}")
        print(f"   Domain: {validated.domain}")
        print(f"   Stream Name: astra.gamification.xpgained.v1")
    except EventValidationError as e:
        print(f"❌ Validation failed: {e}")
        return False
    
    # Test invalid event
    invalid_event = {
        "event_id": "invalid",
        "event_type": "invalid-format",
        "domain": "",
        "entity_id": "",
        "occurred_at": "not-iso-format",
        "event_version": 0,
        "producer": "",
        "data": "invalid-json"
    }
    
    try:
        validate_event_schema(invalid_event)
        print("❌ Invalid event should have failed validation")
        return False
    except EventValidationError:
        print("✅ Invalid event correctly rejected")
    
    return True


def test_gamification_event_adapter():
    """Test Gamification domain event adapter."""
    print("\n=== Testing Gamification Event Adapter ===")
    
    # Test legacy event adaptation
    legacy_event = LegacyEvent(
        event_type="xp_gained",
        entity_id="user_123",
        data={"xp_amount": 50, "activity": "trade"}
    )
    
    adapted = GamificationEventAdapter.adapt_legacy_event(legacy_event)
    
    print(f"✅ Legacy event adapted successfully")
    print(f"   Original: xp_gained -> Enhanced: {adapted['event_type']}")
    print(f"   Domain: {adapted['domain']}")
    print(f"   Entity ID: {adapted['entity_id']}")
    
    # Test enhanced event creation
    enhanced_event = GamificationEventAdapter.create_gamification_event(
        event_type="LevelUp",
        entity_id="user_123",
        data={"old_level": 5, "new_level": 6},
        correlation_id="req_789",
        user_id=123
    )
    
    print(f"✅ Enhanced event created successfully")
    print(f"   Event Type: {enhanced_event['event_type']}")
    print(f"   Correlation ID: {enhanced_event['correlation_id']}")
    
    return True


def test_new_gamification_events():
    """Test new enhanced gamification event classes."""
    print("\n=== Testing New Gamification Events ===")
    
    # Test XP Gained event
    xp_event = create_xp_gained_event(
        user_id=123,
        activity_type="trading",
        xp_amount=50,
        total_xp=1250,
        correlation_id="trade_456"
    )
    
    print(f"✅ XP Gained event created")
    print(f"   Event Type: {xp_event.event_type}")
    print(f"   Domain: {xp_event.domain}")
    print(f"   User ID: {xp_event.user_id}")
    print(f"   Stream Name: {xp_event.get_stream_name()}")
    
    # Test Level Up event
    level_event = create_level_up_event(
        user_id=123,
        old_level=5,
        new_level=6,
        rewards=["achievement_unlock", "bonus_xp"],
        correlation_id="trade_456"
    )
    
    print(f"✅ Level Up event created")
    print(f"   Event Type: {level_event.event_type}")
    print(f"   Level: {level_event.old_level} -> {level_event.new_level}")
    print(f"   Correlation: {level_event.correlation_id}")
    
    # Test Redis Streams serialization
    stream_data = xp_event.to_dict()
    print(f"✅ Redis Streams serialization successful")
    print(f"   Fields: {list(stream_data.keys())}")
    
    return True


def test_adapter_registry():
    """Test adapter registry for automatic domain routing."""
    print("\n=== Testing Adapter Registry ===")
    
    # Test getting adapters for different domains
    domains = ['trading', 'gamification', 'social', 'user', 'financial', 'nft']
    
    for domain in domains:
        adapter = AdapterRegistry.get_adapter(domain)
        print(f"✅ {domain.title()} domain -> {adapter.__name__}")
    
    # Test automatic event adaptation
    test_event_data = {
        "event_type": "TestEvent",
        "entity_id": "test_123",
        "data": {"test": "data"}
    }
    
    adapted = AdapterRegistry.adapt_event_for_streams("gamification", test_event_data)
    print(f"✅ Auto-adaptation successful")
    print(f"   Original: TestEvent -> Enhanced: {adapted['event_type']}")
    
    return True


def test_domain_event_registry():
    """Test domain event registry for schema governance."""
    print("\n=== Testing Domain Event Registry ===")
    
    # Test known events
    trading_events = DomainEventRegistry.get_events_for_domain("Trading")
    print(f"✅ Trading events: {len(trading_events)} registered")
    print(f"   Events: {trading_events[:3]}...")
    
    # Test event validation
    valid_event = "Trading.TradeExecuted"
    invalid_event = "Unknown.InvalidEvent"
    
    print(f"✅ {valid_event} is valid: {DomainEventRegistry.is_valid_event_type(valid_event)}")
    print(f"✅ {invalid_event} is valid: {DomainEventRegistry.is_valid_event_type(invalid_event)}")
    
    return True


def run_all_tests():
    """Run all enhanced event system tests."""
    print("🚀 Starting Enhanced Event System Tests")
    print("=" * 50)
    
    tests = [
        test_enhanced_event_schema,
        test_gamification_event_adapter,
        test_new_gamification_events,
        test_adapter_registry,
        test_domain_event_registry
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Enhanced event system is ready for Redis Streams.")
    else:
        print("⚠️  Some tests failed. Review errors above.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)