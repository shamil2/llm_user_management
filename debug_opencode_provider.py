#!/usr/bin/env python3
"""
Debug script for OpenCode ProviderInitError
This script helps diagnose why OpenCode can't initialize the custom provider
"""

import json
import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_api_server():
    """Check if the API server is running and accessible"""
    print("🔍 Checking API Server")
    print("=" * 20)

    # Try to connect to the API
    success, stdout, stderr = run_command("curl -s http://localhost:8000/", "API connectivity test")

    if success and "LLM User Management API" in stdout:
        print("✅ API server is running and accessible")
        return True
    else:
        print("❌ API server is not accessible")
        print("💡 Start the server with:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False

def check_opencode_config():
    """Check OpenCode configuration"""
    print("\n🔍 Checking OpenCode Configuration")
    print("=" * 35)

    # Common config locations
    config_paths = [
        os.path.expanduser("~/.opencode.json"),
        os.path.expanduser("~/.opencode/config.json"),
        "./opencode.json"
    ]

    config_found = False

    for path in config_paths:
        if os.path.exists(path):
            print(f"✅ Found config file: {path}")
            try:
                with open(path, 'r') as f:
                    config = json.load(f)

                if "models" in config:
                    provider_found = False
                    for model_name, model_config in config["models"].items():
                        if "llm-user-managed" in model_name:
                            provider_found = True
                            print(f"✅ Found LLM provider: {model_name}")

                            # Check configuration
                            api_key = model_config.get("apiKey") or model_config.get("apikey")
                            base_url = model_config.get("baseURL") or model_config.get("baseUrl")

                            if api_key:
                                print(f"✅ API key configured (length: {len(api_key)})")
                            else:
                                print("❌ Missing API key")

                            if base_url:
                                print(f"✅ Base URL: {base_url}")
                                if not base_url.endswith("/v1"):
                                    print("⚠️  Base URL should end with /v1")
                            else:
                                print("❌ Missing baseURL")

                    if not provider_found:
                        print("❌ LLM provider not found in config")
                else:
                    print("❌ No 'models' section in config")

                config_found = True
                break

            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in {path}")
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")

    if not config_found:
        print("❌ No OpenCode configuration file found")
        print("💡 Create ~/.opencode.json with:")

    return config_found

def generate_config():
    """Generate the correct configuration"""
    print("\n🔧 Generating Correct Configuration")
    print("=" * 35)

    # Try to register a test user
    register_cmd = '''curl -s -X POST http://localhost:8000/auth/register \\
  -H "Content-Type: application/json" \\
  -d \'{"username": "opencode_test", "password": "test123", "token_limit": 10000}\''''

    success, stdout, stderr = run_command(register_cmd, "User registration")

    if success:
        try:
            user_data = json.loads(stdout)
            api_key = user_data.get("api_key")
            username = user_data.get("username")

            config = {
                "models": {
                    "llm-user-managed/opencode-llm": {
                        "apiKey": api_key,
                        "baseURL": "http://localhost:8000/v1"
                    }
                }
            }

            print("✅ Configuration generated:")
            print(json.dumps(config, indent=2))
            print(f"\n📝 Test user created: {username}")
            print(f"🔑 API Key: {api_key}")

            # Suggest config location
            config_path = os.path.expanduser("~/.opencode.json")
            print(f"\n💡 Save this to: {config_path}")

            return config

        except json.JSONDecodeError:
            print(f"❌ Invalid response from API: {stdout}")
    else:
        print("❌ Failed to register test user")
        print(f"Error: {stderr}")

        # Provide manual configuration
        print("\n📋 Manual Configuration:")
        config = {
            "models": {
                "llm-user-managed/opencode-llm": {
                    "apiKey": "your-api-key-here",
                    "baseURL": "http://localhost:8000/v1"
                }
            }
        }
        print(json.dumps(config, indent=2))
        print("\n🔑 Get API key by running:")
        print("curl -X POST http://localhost:8000/auth/register -H 'Content-Type: application/json' -d '{\"username\": \"your_name\", \"password\": \"your_password\", \"token_limit\": 10000}'")

    return None

def main():
    """Main debugging function"""
    print("🐛 OpenCode ProviderInitError Debugger")
    print("=====================================\n")

    # Check API server
    api_ok = check_api_server()

    # Check OpenCode configuration
    config_ok = check_opencode_config()

    # Generate correct configuration
    if api_ok:
        generate_config()

    # Provide troubleshooting steps
    print("\n🔧 Troubleshooting Steps:")
    print("=" * 23)
    print("1. ✅ Start API server on port 8000")
    print("2. ✅ Create ~/.opencode.json with correct configuration")
    print("3. ✅ Use a valid API key from user registration")
    print("4. ✅ Ensure baseURL ends with /v1")
    print("5. ✅ Restart OpenCode after configuration changes")

    print("\n🚨 Common ProviderInitError Causes:")
    print("=" * 35)
    print("• API server not running")
    print("• Wrong port (should be 8000, not 8002)")
    print("• Invalid or missing API key")
    print("• Incorrect baseURL format")
    print("• Firewall blocking localhost connections")
    print("• OpenCode configuration file in wrong location")

    print("\n🔄 Alternative Methods:")
    print("=" * 22)
    print("• Environment variables:")
    print("  export OPENAI_API_KEY='your-key'")
    print("  export OPENAI_BASE_URL='http://localhost:8000/v1'")
    print("• Try different config locations:")
    print("  ~/.opencode.json")
    print("  ~/.opencode/config.json")

if __name__ == "__main__":
    main()