# OpenCode Model Provider Configuration

This guide shows how to configure OpenCode to use your LLM User Management API as a model provider, similar to other LLM services.

## Configuration Steps

### 1. Set Up Your API

First, ensure your API is running with the OpenAI-compatible endpoints:

```bash
# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your VLLM_ENDPOINT and other settings

# Create database tables
PYTHONPATH=. python scripts/create_tables.py

# Create a test user (optional)
PYTHONPATH=. python scripts/create_test_user.py

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Register a User and Get API Key

```bash
# Register a user (this will generate an API key)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "opencode_model",
    "password": "secure_password_123",
    "token_limit": 50000
  }'

# Response will include your API key:
# {
#   "id": 1,
#   "username": "opencode_model",
#   "token_limit": 50000,
#   "tokens_used": 0,
#   "api_key": "your_generated_api_key_here"
# }
```

### 3. Configure OpenCode

Add your API as a model provider in OpenCode's configuration. The exact configuration method depends on your OpenCode setup, but here are common approaches:

#### Option A: Environment Variables (if supported)
```bash
export OPENAI_API_BASE="http://localhost:8000/v1"
export OPENAI_API_KEY="your_api_key_from_registration"
```

#### Option B: Configuration File
Create or edit your OpenCode configuration file:

```json
{
  "models": {
    "llm-user-managed": {
      "provider": "openai",
      "base_url": "http://localhost:8000/v1",
      "api_key": "your_api_key_from_registration",
        "model": "mistralai/Devstral-2-123B-Instruct-2512"
    }
  },
  "default_model": "mistralai/Devstral-2-123B-Instruct-2512"
}
```

#### Option C: Direct Integration
If OpenCode allows custom model configurations, add:

```python
# In your OpenCode configuration
MODEL_CONFIGS = {
    "llm-user-managed": {
        "api_base": "http://localhost:8000/v1",
        "api_key": "your_api_key_from_registration",
        "model_name": "mistralai/Devstral-2-123B-Instruct-2512"
    }
}
```

### 4. Test the Integration

Test that OpenCode can communicate with your API:

```bash
# Test the models endpoint
curl -H "Authorization: Bearer your_api_key" \
  http://localhost:8000/v1/models

# Test a completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llm-user-managed",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 50
  }'
```

### 5. Usage in OpenCode

Once configured, you can use your model in OpenCode:

```
# Set the model
/model mistralai/Devstral-2-123B-Instruct-2512

# Or use it directly in conversations
Hello, can you help me write a Python function?
```

## API Key Management

### View Your API Key
```bash
curl -H "Authorization: Bearer your_jwt_token" \
  http://localhost:8000/users/me
```

### Regenerate API Key (if needed)
Currently, API keys are generated during registration. For key rotation, you would need to implement a key regeneration endpoint.

## Monitoring Usage

### Check Token Usage
```bash
curl -H "Authorization: Bearer your_jwt_token" \
  http://localhost:8000/users/usage
```

### Monitor API Logs
```bash
tail -f server.log
```

## Security Considerations

1. **API Key Protection**: Never commit API keys to version control
2. **HTTPS**: Use HTTPS in production environments
3. **Rate Limiting**: The API includes token-based rate limiting
4. **Token Limits**: Monitor usage to avoid hitting limits

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check API key is correct
   - Ensure "Bearer " prefix in Authorization header

2. **429 Token Limit Exceeded**
   - Check usage: `GET /users/usage`
   - Request limit increase or reset usage

3. **502 vLLM Service Error**
   - Ensure vLLM is running and accessible
   - Check vLLM endpoint configuration

4. **Model Not Available in OpenCode**
   - Verify OpenCode configuration
   - Check that API server is running
   - Confirm API key is set correctly

### Debug Commands

```bash
# Test API connectivity
curl http://localhost:8000/v1/models

# Test with API key
curl -H "Authorization: Bearer your_key" \
  http://localhost:8000/v1/models

# Check server logs
tail -f server.log
```

## Advanced Configuration

### Multiple Models
You can set up multiple model providers:

```json
{
  "models": {
    "llm-user-managed-gpt": {
      "provider": "openai",
      "base_url": "http://localhost:8000/v1",
      "api_key": "api_key_1",
        "model": "mistralai/Devstral-2-123B-Instruct-2512"
    },
    "llm-user-managed-claude": {
      "provider": "openai", 
      "base_url": "http://localhost:8000/v1",
      "api_key": "api_key_2",
        "model": "mistralai/Devstral-2-123B-Instruct-2512"
    }
  }
}
```

### Load Balancing
For high availability, deploy multiple API instances and configure OpenCode to use different endpoints based on load or region.

This setup allows OpenCode to use your authenticated LLM API as seamlessly as any other model provider, with full usage tracking and security features.</content>
<parameter name="filePath">OPENCODE_MODEL_INTEGRATION.md