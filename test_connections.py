#!/usr/bin/env python3
"""
DIX VISION Connection Test Script
Tests the connection between React dashboard and Python backend
"""

import sys
import time
import requests
import asyncio
import websockets

# Configuration
API_BASE_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080"

def test_api_connection():
    """Test if the Python backend API is responding"""
    print("Testing API connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ API connection successful")
            print(f"  Health check: {response.json()}")
            return True
        else:
            print(f"✗ API connection failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ API connection failed: {e}")
        return False

def test_websocket_connection():
    """Test WebSocket connection"""
    print("\nTesting WebSocket connection...")
    async def ws_test():
        try:
            async with websockets.connect(f"{WS_URL}/ws/system/status") as ws:
                print("✓ WebSocket connection successful")
                await ws.send(json.dumps({"type": "ping"}))
                response = await ws.recv()
                print(f"  Server response: {response}")
                return True
        except Exception as e:
            print(f"✗ WebSocket connection failed: {e}")
            return False
    
    return asyncio.run(ws_test())

def test_state_projection():
    """Test StateProjection endpoint"""
    print("\nTesting StateProjection endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/state-projection", timeout=5)
        if response.status_code == 200:
            print("✓ StateProjection endpoint accessible")
            state = response.json()
            print(f"  Current mode: {state.get('current_mode', 'unknown')}")
            print(f"  System health: {state.get('system_health', {}).get('overall_status', 'unknown')}")
            return True
        else:
            print(f"✗ StateProjection endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ StateProjection test failed: {e}")
        return False

def test_engine_registry():
    """Test engine registry"""
    print("\nTesting engine registry...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/registry/engines", timeout=5)
        if response.status_code == 200:
            print("✓ Engine registry accessible")
            registry = response.json()
            print(f"  Engines: {list(registry.keys())}")
            return True
        else:
            print(f"✗ Engine registry failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Engine registry test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("DIX VISION Backend Connection Test")
    print("=" * 60)
    
    results = {
        "API Connection": test_api_connection(),
        "StateProjection": test_state_projection(),
        "Engine Registry": test_engine_registry(),
        # WebSocket test requires additional setup
    }
    
    print("\n" + "=" * 60)
    print("Connection Test Results")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("All connection tests passed! ✓")
        print("The React dashboard should be able to connect to the backend.")
        return 0
    else:
        print("Some connection tests failed. ✗")
        print("Please ensure the Python backend is running: uvicorn ui.server:app --reload")
        return 1

if __name__ == "__main__":
    sys.exit(main())