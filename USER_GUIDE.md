# User Guide: LLM User Management API

This guide explains how to use the LLM User Management API to access vLLM services with user authentication and token tracking.

## Prerequisites

- Access to a running LLM User Management API server
- A tool for making HTTP requests (curl, Postman, or any HTTP client)

## Step 1: Register a User Account

First, create a new user account by registering with the API.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password",
  "token_limit": 10000
}
```

**Note:** Passwords cannot exceed 72 bytes in length (approximately 72 characters for ASCII, fewer for Unicode characters).

**Example using curl:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123",
    "token_limit": 10000
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "token_limit": 10000,
  "tokens_used": 0
}
```

## Step 2: Log In to Get Access Token

Authenticate with your credentials to receive a JWT access token for API access.

**Endpoint:** `POST /auth/token`

**Request (OAuth2 Form):**
- Content-Type: `application/x-www-form-urlencoded`
- Fields: `username`, `password`

**Example using curl:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=secure_password123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Important:** Save the `access_token` value for use in subsequent requests.

## Step 3: Use vLLM Completions

Make authenticated requests to the vLLM completions endpoint. The API will proxy your request to the underlying vLLM service while tracking token usage.

**Endpoint:** `POST /chat/completions`

**Headers:**
- `Authorization: Bearer <your_access_token>`
- `Content-Type: application/json`

**Request Body:** Standard OpenAI-compatible completions format
```json
{
  "prompt": "Hello, how are you?",
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Example using curl:**
```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

**Response:** vLLM response (OpenAI-compatible format)
```json
{
  "id": "cmpl-123",
  "object": "text_completion",
  "created": 1677652288,
  "model": "your-model",
  "choices": [
    {
      "text": "Hello! I'm doing well, thank you for asking. How can I help you today?",
      "index": 0,
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 15,
    "total_tokens": 20
  }
}
```

## Step 4: Check Token Usage

Monitor your token usage to avoid hitting limits.

**Endpoint:** `GET /users/usage`

**Headers:**
- `Authorization: Bearer <your_access_token>`

**Example using curl:**
```bash
curl -X GET http://localhost:8000/users/usage \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "tokens_used": 125,
  "token_limit": 10000,
  "remaining": 9875
}
```

## Step 5: Refresh Access Token (Optional)

If your token expires, refresh it without re-entering credentials.

**Endpoint:** `POST /auth/refresh`

**Headers:**
- `Authorization: Bearer <your_current_token>`

**Example using curl:**
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Error Handling

### Common Errors

- **401 Unauthorized:** Invalid or expired token. Log in again.
- **429 Too Many Requests:** Token limit exceeded. Check usage and contact admin if needed.
- **400 Bad Request:** Invalid request format or username already exists.
- **502 Bad Gateway:** vLLM service is unavailable.

### Token Limits

- Each user has a configurable token limit (default: 10,000 tokens)
- Token counting is based on prompt length (approximated)
- Usage is tracked per user and cannot be reset without admin intervention

## API Documentation

For complete API documentation, visit the interactive docs at:
`http://your-api-server/docs`

## Troubleshooting

1. **Can't register:** Username may already be taken
2. **Can't log in:** Check username/password spelling
3. **Token expired:** Use refresh endpoint or log in again
4. **Token limit exceeded:** Check usage and request limit increase
5. **vLLM errors:** Check that the vLLM service is running and accessible

## Support

If you encounter issues, check the server logs or contact your system administrator.