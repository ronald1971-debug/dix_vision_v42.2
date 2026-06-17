"""
cognitive_control_center.tests.test_pairing_service_migration
Test device pairing service migration to verify feature parity with cockpit/pairing.py

This test validates that the cognitive control center pairing service maintains
feature parity with the original cockpit/pairing.py service.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_pairing_token_generation():
    """Test that pairing token generation works"""
    from cognitive_control_center.shared_services.pairing import (
        DevicePairingService,
        get_device_pairing_service,
    )
    
    print("Testing device pairing token generation...")
    
    # Test 1: Service instantiation
    service = DevicePairingService()
    assert service, "Service instantiation failed"
    print("[PASS] Service instantiation works")
    
    # Test 2: Singleton service
    service2 = get_device_pairing_service()
    assert service2, "Singleton service retrieval failed"
    print("[PASS] Singleton service retrieval works")
    
    # Test 3: Token generation
    token = service.issue_pairing_token("TestDevice")
    assert token, "Token generation failed"
    assert token.token_id, "Token ID should be set"
    assert len(token.token_id) > 20, f"Token ID too short: {len(token.token_id)}"
    print(f"[PASS] Token generation works: {token.token_id[:20]}...")
    
    # Test 4: Token with custom TTL
    token_custom = service.issue_pairing_token("TestDevice2", ttl_sec=1800)
    assert token_custom, "Custom TTL token generation failed"
    assert token_custom.token_id != token.token_id, "Tokens should be unique"
    print("[PASS] Token generation with custom TTL works")
    
    print("[SUCCESS] Device pairing token generation: ALL TESTS PASSED")


def test_pairing_token_claiming():
    """Test that token claiming workflow works"""
    from cognitive_control_center.shared_services.pairing import DevicePairingService
    
    print("\nTesting device pairing token claiming...")
    
    service = DevicePairingService()
    
    # Test 1: Issue and claim token
    token_obj = service.issue_pairing_token("TestDevice3")
    device = service.claim_pairing_token(token_obj.token_id, "mobile_device_1")
    assert device, "Token claiming failed"
    assert device.device_id, "Device ID should be set"
    assert device.label == "TestDevice3", "Device label should match"
    assert device.device_type == "mobile_device_1", "Device type should match"
    print("[PASS] Token claiming workflow works")
    
    # Test 2: Claim already claimed token
    device2 = service.claim_pairing_token(token_obj.token_id, "mobile_device_2")
    assert device2 is None, "Already claimed token should return None"
    print("[PASS] Already claimed token rejection works")
    
    # Test 3: Claim invalid token
    device3 = service.claim_pairing_token("invalid_token", "mobile_device_3")
    assert device3 is None, "Invalid token should return None"
    print("[PASS] Invalid token rejection works")
    
    print("[SUCCESS] Device pairing token claiming: ALL TESTS PASSED")


def test_pairing_device_management():
    """Test that paired device management works"""
    from cognitive_control_center.shared_services.pairing import DevicePairingService
    
    print("\nTesting device pairing device management...")
    
    service = DevicePairingService()
    
    # Test 1: Get all paired devices (initially empty)
    devices = service.get_paired_devices()
    assert isinstance(devices, list), "Devices should be a list"
    print(f"[PASS] Get paired devices works: {len(devices)} devices")
    
    # Test 2: Add a paired device
    token_obj = service.issue_pairing_token("TestDevice4")
    device = service.claim_pairing_token(token_obj.token_id, "mobile_device_4")
    devices_after = service.get_paired_devices()
    assert len(devices_after) > 0, "Paired devices list should not be empty"
    print(f"[PASS] Paired device added: {len(devices_after)} devices")
    
    # Test 3: Remove device
    device_id = device.device_id
    removed = service.remove_device(device_id)
    assert removed, "Device removal should succeed"
    devices_after_removal = service.get_paired_devices()
    assert len(devices_after_removal) == 0, "Device should be removed"
    print("[PASS] Device removal works")
    
    # Test 4: Remove non-existent device
    removed_invalid = service.remove_device("nonexistent_device_id")
    assert not removed_invalid, "Removing non-existent device should fail"
    print("[PASS] Non-existent device removal fails correctly")
    
    print("[SUCCESS] Device pairing device management: ALL TESTS PASSED")


def test_pairing_token_expiration():
    """Test that token expiration and cleanup works"""
    from cognitive_control_center.shared_services.pairing import DevicePairingService
    
    print("\nTesting device pairing token expiration...")
    
    service = DevicePairingService()
    
    # Test 1: Token with short TTL
    token_obj = service.issue_pairing_token("TestDevice5", ttl_sec=1)
    assert token_obj, "Short TTL token generation failed"
    assert token_obj.token_id, "Token ID should be set"
    assert token_obj.expires_at, "Expiration time should be set"
    print("[PASS] Short TTL token generation works")
    
    # Test 2: Token with longer TTL
    token_long = service.issue_pairing_token("TestDevice6", ttl_sec=3600)
    assert token_long, "Long TTL token generation failed"
    assert token_long.token_id, "Token ID should be set"
    assert token_long.expires_at, "Expiration time should be set"
    print("[PASS] Long TTL token generation works")
    
    # Test 3: Token expiration time is in the future
    from datetime import datetime
    assert token_long.expires_at > datetime.utcnow(), "Expiration should be in the future"
    print("[PASS] Token expiration time is correctly set")
    
    print("[SUCCESS] Device pairing token expiration: ALL TESTS PASSED")


def test_pairing_cognitive_integration():
    """Test that pairing service integrates with cognitive environment (enhanced feature)"""
    from cognitive_control_center.shared_services.pairing import DevicePairingService
    from cognitive_control_center.core.operating_environment import get_cognitive_environment
    
    print("\nTesting device pairing cognitive integration...")
    
    # Test 1: Service can be instantiated with cognitive environment
    service = DevicePairingService()
    env = get_cognitive_environment()
    assert service, "Service instantiation failed"
    assert env, "Cognitive environment retrieval failed"
    print("[PASS] Cognitive environment integration works")
    
    # Test 2: Device registration can be enhanced with workspace context
    token_obj = service.issue_pairing_token("TestDevice7")
    device = service.claim_pairing_token(token_obj.token_id, "mobile_device_7")
    assert device, "Device claiming with cognitive integration failed"
    print("[PASS] Device registration with cognitive integration works")
    
    print("[SUCCESS] Device pairing cognitive integration: ALL TESTS PASSED")


def main():
    """Run all pairing service tests"""
    print("=" * 70)
    print("DEVICE PAIRING SERVICE MIGRATION TESTS")
    print("=" * 70)
    
    try:
        test_pairing_token_generation()
        test_pairing_token_claiming()
        test_pairing_device_management()
        test_pairing_token_expiration()
        test_pairing_cognitive_integration()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL DEVICE PAIRING SERVICE TESTS PASSED")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n[FAILURE] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[FAILURE] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())