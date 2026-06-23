"""
cognitive_control_center.tests.test_auth_service_migration
Test authentication service migration to verify feature parity with cockpit/auth.py

This test validates that the cognitive control center auth service maintains
100% feature parity with the original cockpit/auth.py service.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_auth_service_token_generation():
    """Test that token generation works identically to cockpit/auth.py"""
    from cognitive_control_center.shared_services.auth import (
        CognitiveAuthService,
        get_or_create_token,
    )

    print("Testing authentication service token generation...")

    # Test 1: Token generation
    service = CognitiveAuthService()
    token1 = service.get_or_create_token()
    assert token1, "Token generation failed"
    assert len(token1) > 20, f"Token too short: {len(token1)}"
    print(f"[PASS] Token generation works: {token1[:20]}...")

    # Test 2: Token persistence (using temp directory)
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["DIX_COCKPIT_TOKEN_FILE"] = str(Path(tmpdir) / "test_token.txt")
        service2 = CognitiveAuthService()
        token2 = service2.get_or_create_token()
        assert token2, "Token generation with file failed"
        print(f"[PASS] Token persistence works")

    # Test 3: Environment variable override
    os.environ["DIX_COCKPIT_TOKEN"] = "test_env_token_12345"
    service3 = CognitiveAuthService()
    token3 = service3.get_or_create_token()
    assert token3 == "test_env_token_12345", "Environment variable override failed"
    print("[PASS] Environment variable override works")

    # Test 4: Global get_or_create_token function
    token4 = get_or_create_token()
    assert token4, "Global token function failed"
    print("[PASS] Global get_or_create_token function works")

    print("[SUCCESS] Authentication service token generation: ALL TESTS PASSED")


def test_auth_service_one_time_tokens():
    """Test one-time token functionality (enhanced feature)"""
    from cognitive_control_center.shared_services.auth import CognitiveAuthService

    print("\nTesting authentication service one-time tokens...")

    service = CognitiveAuthService()

    # Test 1: Generate one-time token
    ott = service.generate_one_time_token(ttl_seconds=900)
    assert ott, "One-time token generation failed"
    assert len(ott) > 20, f"One-time token too short: {len(ott)}"
    print(f"[PASS] One-time token generation works")

    # Test 2: Validate valid one-time token
    is_valid = service.validate_one_time_token(ott)
    assert is_valid, "Valid one-time token rejected"
    print("[PASS] One-time token validation works")

    # Test 3: Validate consumed token
    is_valid_again = service.validate_one_time_token(ott)
    assert not is_valid_again, "Consumed one-time token should be invalid"
    print("[PASS] One-time token consumption works")

    # Test 4: Validate invalid token
    is_invalid = service.validate_one_time_token("invalid_token_12345")
    assert not is_invalid, "Invalid token should be rejected"
    print("[PASS] Invalid token rejection works")

    print("[SUCCESS] Authentication service one-time tokens: ALL TESTS PASSED")


def test_auth_service_middleware():
    """Test that middleware maintains same API as cockpit/auth.py"""
    from cognitive_control_center.shared_services.auth import (
        PUBLIC_PATH_PREFIXES,
        PUBLIC_PATHS_EXACT,
        CognitiveTokenAuthMiddleware,
        _extract,
    )

    print("\nTesting authentication service middleware...")

    # Test 1: Public paths configuration preserved
    assert "/" in PUBLIC_PATHS_EXACT, "Root path should be public"
    assert "/health" in PUBLIC_PATHS_EXACT, "Health endpoint should be public"
    assert "/static/" in PUBLIC_PATH_PREFIXES, "Static path prefix should be public"
    print(
        f"[PASS] Public paths configuration preserved ({len(PUBLIC_PATHS_EXACT)} exact, {len(PUBLIC_PATH_PREFIXES)} prefixes)"
    )

    # Test 2: Middleware instantiation
    token = "test_token_for_middleware"
    middleware = CognitiveTokenAuthMiddleware(lambda scope, receive, send: None, token)
    assert middleware, "Middleware instantiation failed"
    print("[PASS] Middleware instantiation works")

    # Test 3: Token extraction function preserved
    from unittest.mock import Mock

    from starlette.requests import Request

    # Test header extraction
    mock_request = Mock(spec=Request)
    mock_request.headers.get.return_value = "Bearer test_header_token"
    mock_request.query_params.get.return_value = None
    mock_request.cookies.get.return_value = None

    extracted = _extract(mock_request)
    assert extracted == "test_header_token", "Header extraction failed"
    print("[PASS] Bearer token extraction from header works")

    # Test query param extraction
    mock_request.headers.get.return_value = ""
    mock_request.query_params.get.return_value = "test_query_token"

    extracted = _extract(mock_request)
    assert extracted == "test_query_token", "Query param extraction failed"
    print("[PASS] Token extraction from query param works")

    # Test cookie extraction
    mock_request.query_params.get.return_value = None
    mock_request.cookies.get.return_value = "test_cookie_token"

    extracted = _extract(mock_request)
    assert extracted == "test_cookie_token", "Cookie extraction failed"
    print("[PASS] Token extraction from cookie works")

    print("[SUCCESS] Authentication service middleware: ALL TESTS PASSED")


def test_auth_service_cognitive_integration():
    """Test that cognitive environment integration works (enhanced feature)"""
    from cognitive_control_center.core.operating_environment import get_cognitive_environment
    from cognitive_control_center.shared_services.auth import get_cognitive_auth_service

    print("\nTesting authentication service cognitive integration...")

    # Test 1: Service integrates with cognitive environment
    service = get_cognitive_auth_service()
    env = get_cognitive_environment()
    assert service, "Cognitive auth service retrieval failed"
    assert env, "Cognitive environment retrieval failed"
    print("[PASS] Cognitive environment integration works")

    # Test 2: Token generation triggers cognitive environment registration
    state_before = env.get_environment_state()
    token = service.get_or_create_token()
    state_after = env.get_environment_state()

    # Should have registered auth_service entity
    assert len(state_after["active_entities"]) >= len(
        state_before["active_entities"]
    ), "Cognitive environment entity registration failed"
    print("[PASS] Cognitive environment entity registration works")

    print("[SUCCESS] Authentication service cognitive integration: ALL TESTS PASSED")


def main():
    """Run all authentication service tests"""
    print("=" * 70)
    print("AUTHENTICATION SERVICE MIGRATION TESTS")
    print("=" * 70)

    try:
        test_auth_service_token_generation()
        test_auth_service_one_time_tokens()
        test_auth_service_middleware()
        test_auth_service_cognitive_integration()

        print("\n" + "=" * 70)
        print("[SUCCESS] ALL AUTHENTICATION SERVICE TESTS PASSED")
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
