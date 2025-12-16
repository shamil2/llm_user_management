# LLM User Management API

A FastAPI application that provides authenticated access to vLLM instances with token usage tracking.

## Features

- User registration and authentication with JWT tokens
- Token usage tracking per user
- Proxy requests to vLLM with authentication
- User management endpoints
- Configurable token limits
- **OpenAI-compatible API** for direct integration with opencode

## Quick Start

1. Set up Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment configuration:
```bash
cp .env.example .env
```

4. Create database tables:
```bash
python scripts/create_tables.py
```

4. Start the OpenAI-compatible API server:
```bash
python opencode_provider_flask.py
```

The API will be available at `http://localhost:8002`

## OpenCode Integration

Integrate this API directly with opencode as a custom model provider:

### 1. Configure opencode

Add to your `opencode.json`:

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

### 2. Add API Key to opencode

```bash
# In opencode, connect to the custom provider
/connect
# Select "Other" and enter provider ID: llm-user-managed
# Enter API key: 6AKHFK3uQw3Z2LzkC0uXSE2C5k_wnnJuEyvI4ul0wMc
```

### 3. Use the Model

```bash
# In opencode
/models
# Select: llm-user-managed/opencode-llm
```

## API Endpoints

### Authentication (JWT-based)
- `POST /auth/register` - Register a new user
- `POST /auth/token` - Login and get access token
- `POST /auth/refresh` - Refresh access token

### Chat (JWT authenticated)
- `POST /chat/completions` - Proxy to vLLM completions endpoint

### User Management (JWT authenticated)
- `GET /users/me` - Get current user info
- `PUT /users/me/token-limit` - Update token limit
- `GET /users/usage` - Get token usage statistics

### OpenAI-Compatible (API key authenticated)
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - OpenAI-compatible chat completions
- `POST /v1/completions` - OpenAI-compatible completions

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/token` - Login and get access token
- `POST /auth/refresh` - Refresh access token

### Chat (requires authentication)
- `POST /chat/completions` - Proxy to vLLM completions endpoint

### User Management (requires authentication)
- `GET /users/me` - Get current user info
- `PUT /users/me/token-limit` - Update token limit
- `GET /users/usage` - Get token usage statistics

## Environment Variables

See `.env.example` for required configuration.

## Development

- Run tests: `pytest tests/ -v`
- Type checking: `mypy app/ --ignore-missing-imports`
- Linting: `flake8 app/ && black app/ && isort app/`
- Start API server: `python opencode_provider_flask.py`