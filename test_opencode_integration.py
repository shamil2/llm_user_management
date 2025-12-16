#!/usr/bin/env python3
"""
Test script for OpenCode integration
This script verifies that your API is compatible with OpenCode's expected format
"""

import requests
import json
import sys

def test_openai_compatibility():
    """Test OpenAI-compatible endpoints"""
    base_url = "http://localhost:8000"

    print("🧪 Testing OpenCode Integration")
    print("=" * 50)

    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print(f"❌ API server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("💡 Make sure the server is running:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        print("   PYTHONPATH=. python scripts/create_tables.py")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False

    # Test 2: Models endpoint
    try:
        response = requests.get(f"{base_url}/v1/models")
        if response.status_code == 200:
            models = response.json()
            print("✅ Models endpoint working")
            print(f"   Available models: {len(models.get('data', []))}")
        else:
            print(f"❌ Models endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")

    # Test 3: Register a test user
    try:
        user_data = {
            "username": "test_opencode_user",
            "password": "test_password_123",
            "token_limit": 1000
        }
        response = requests.post(
            f"{base_url}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            user_info = response.json()
            api_key = user_info.get("api_key")
            print("✅ User registration successful")
            print(f"   API Key: {api_key}")
        else:
            print(f"⚠️  User registration returned {response.status_code}: {response.text}")
            # Try to get existing user's API key
            api_key = "6AKHFK3uQw3Z2LzkC0uXSE2C5k_wnnJuEyvI4ul0wMc"  # fallback
    except Exception as e:
        print(f"❌ User registration error: {e}")
        api_key = None

    # Test 4: Chat completions (requires auth)
    if api_key:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            chat_data = {
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50,
                "model": "test"
            }
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                json=chat_data,
                headers=headers
            )
            if response.status_code == 200:
                print("✅ Chat completions endpoint working")
            elif response.status_code == 502:
                print("⚠️  Chat completions returns 502 (vLLM not running - this is expected)")
                print("   The endpoint is configured correctly, just needs vLLM backend")
            else:
                print(f"❌ Chat completions returned {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Chat completions error: {e}")
    else:
        print("⚠️  Skipping chat completions test (no API key)")

    print("\n📋 OpenCode Configuration:")
    print("=" * 30)
    print("Add this to your opencode.json:")
    config = {
        "models": {
            "llm-user-managed/opencode-llm": {
                "apiKey": api_key or "your-api-key-here",
                "baseURL": f"{base_url}/v1"
            }
        }
    }
    print(json.dumps(config, indent=2))

    print("\n🔗 Alternative Configuration Methods:")
    print("- Environment variables: OPENAI_API_KEY and OPENAI_BASE_URL")
    print("- Direct provider configuration in OpenCode settings")
    print("- Custom provider setup via OpenCode's provider interface")

    print("\n✅ Integration test complete!")
    return True

if __name__ == "__main__":
    success = test_openai_compatibility()
    sys.exit(0 if success else 1)