# OpenCode Model Provider Setup

Follow these steps to integrate your LLM API as a model provider in OpenCode using the custom provider configuration.

## Step 1: Set Up the OpenAI-Compatible API Server

Start the FastAPI-based OpenAI-compatible API server:

```bash
# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env to set your VLLM_ENDPOINT

# Create database tables
PYTHONPATH=. python scripts/create_tables.py

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

The OpenAI-compatible endpoints will be available at `http://localhost:8000/v1/`

## Step 2: Test the Provider

```bash
# Test models endpoint
curl http://localhost:8002/v1/models

# Test chat completion (requires vLLM running on port 8001)
curl -X POST http://localhost:8002/v1/chat/completions \
  -H "Authorization: Bearer 6AKHFK3uQw3Z2LzkC0uXSE2C5k_wnnJuEyvI4ul0wMc" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "opencode-llm",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 10
  }'
```
```

## Step 3: Configure OpenCode

### Add Custom Provider to opencode.json

Create or edit your `opencode.json` configuration file:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "llm-user-managed": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LLM User Management API",
      "options": {
        "baseURL": "http://localhost:8002/v1"
      },
      "models": {
        "opencode-llm": {
          "name": "Managed LLM API"
        }
      }
    }
  }
}
```

### Connect API Key in OpenCode

```bash
# In OpenCode TUI, run:
/connect

# Select "Other"
# Enter provider ID: llm-user-managed
# Enter API key: 6AKHFK3uQw3Z2LzkC0uXSE2C5k_wnnJuEyvI4ul0wMc
```

## Step 4: Use in OpenCode

Select your model in OpenCode:

```bash
# In OpenCode TUI
/models

# Select: llm-user-managed/opencode-llm
```

## Features

✅ **OpenAI-Compatible API**: Full compatibility with OpenCode
✅ **API Key Authentication**: Secure access control
✅ **Token Tracking**: Usage monitoring and limits
✅ **Error Handling**: Proper HTTP status codes

## Troubleshooting

**401 Unauthorized**: Check API key in `/connect` command
**502 Bad Gateway**: Ensure vLLM is running on configured endpoint
**Model not showing**: Verify opencode.json configuration

### "502 Bad Gateway"
- Verify vLLM is running and accessible
- Check VLLM_ENDPOINT configuration

### Model not appearing in OpenCode
- Verify OpenCode configuration
- Check that provider server is running
- Confirm API key is set correctly

### Connection refused
- Ensure provider server is running on port 8002
- Check firewall settings

## Advanced Configuration

### Multiple Models
```json
{
  "models": {
    "opencode-llm-gpt": {
      "provider": "openai",
      "base_url": "http://localhost:8002/v1",
      "api_key": "key1",
      "model": "opencode-llm"
    },
    "opencode-llm-claude": {
      "provider": "openai", 
      "base_url": "http://localhost:8002/v1",
      "api_key": "key2",
      "model": "opencode-llm"
    }
  }
}
```

### Load Balancing
Deploy multiple provider instances behind a load balancer for high availability.

This setup gives you a clean, OpenAI-compatible API that OpenCode can use directly as a model provider, without the complexity of MCP servers.