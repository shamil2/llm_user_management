# Main API Application - AGENTS.md

## Package Identity
- **Purpose**: FastAPI application that proxies requests to vLLM while handling user authentication and token usage tracking
- **Tech**: FastAPI with SQLAlchemy ORM, JWT authentication, middleware for token counting

## Setup & Run
- Install: `pip install -r requirements.txt` (from root)
- Dev server: `uvicorn app.main:app --reload`
- Build: N/A (Python project)
- Test: `pytest tests/ -v`
- Lint/typecheck: `flake8 app/ && mypy app/`

## Patterns & Conventions
**File Organization**:
- `app/main.py` - FastAPI app instance and startup
- `app/routers/` - API route handlers (auth, chat, users)
- `app/models/` - SQLAlchemy database models (User, TokenUsage)
- `app/middleware/` - Custom middleware (auth, token counting)
- `app/dependencies/` - FastAPI dependencies (get_current_user, get_db)
- `app/config.py` - Settings and environment config
- `app/utils/` - Helper functions (token counting, JWT utils)

**Naming Conventions**:
- Routes: snake_case (`/auth/login`, `/chat/completions`)
- Models: PascalCase classes (`User`, `TokenUsage`)
- Functions: snake_case (`get_current_user`, `count_tokens`)
- Files: snake_case (`auth_router.py`, `user_model.py`)

**Preferred Patterns**:
- ✅ Auth middleware: Always apply `AuthMiddleware` to protected routes
- ❌ No auth bypass: Never skip auth for `/chat/*` endpoints
- ✅ Token counting: Use `TokenCountingMiddleware` on all vLLM proxy routes
- ✅ Database sessions: Use `get_db()` dependency for all DB operations
- ✅ Error handling: Raise `HTTPException` with appropriate status codes
- ✅ User context: Pass `current_user: User` in route dependencies

## Touch Points / Key Files
- Auth logic: `app/routers/auth.py` (JWT token creation/validation)
- User model: `app/models/user.py` (User table with token limits)
- Token counting: `app/middleware/token_counter.py` (tracks usage per request)
- vLLM proxy: `app/routers/chat.py` (proxies requests to vLLM instance)
- Database config: `app/config.py` (connection strings, vLLM endpoint)

## JIT Index Hints
- Find route handlers: `grep -rn "def " app/routers/ | grep -E "@router\.(get|post|put|delete)"`
- Find middleware classes: `grep -rn "class.*Middleware" app/middleware/`
- Find database models: `grep -rn "class.*Base" app/models/`
- Find dependencies: `grep -rn "def get_" app/dependencies/`

## Common Gotchas
- JWT secrets must be 32+ characters for HS256
- Always check `user.token_limit` before allowing requests
- vLLM endpoint must be reachable from API server
- Database migrations run via `scripts/migrate.py` before startup

## Best Practices for FastAPI Development

### API Design
- **RESTful Endpoints**: Use proper HTTP methods (GET, POST, PUT, DELETE)
- **Status Codes**: Return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 429, 500)
- **Error Responses**: Use consistent error response format with `detail` field
- **Pagination**: Implement pagination for list endpoints when needed
- **Versioning**: Use URL versioning (`/v1/`) for API versions

### Authentication & Security
- **JWT Tokens**: Use short-lived access tokens (24h) with refresh tokens
- **Password Security**: Hash passwords with bcrypt, validate strength
- **API Keys**: Generate secure random API keys for users
- **Rate Limiting**: Implement token-based rate limiting
- **Input Validation**: Use Pydantic models for all request/response data

### Database Patterns
- **SQLAlchemy ORM**: Use declarative base with proper relationships
- **Session Management**: Use dependency injection for database sessions
- **Migrations**: Use Alembic for database schema changes
- **Connection Pooling**: Configure proper connection limits
- **Indexes**: Add database indexes for frequently queried fields

### Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints with database
- **Authentication Tests**: Test protected endpoints
- **Error Handling**: Test error conditions and edge cases
- **Coverage**: Aim for >80% code coverage

### Performance Considerations
- **Async Operations**: Use async/await for I/O operations
- **Database Queries**: Optimize queries, use select_related/prefetch
- **Caching**: Implement caching for frequently accessed data
- **Background Tasks**: Use background tasks for non-blocking operations
- **Resource Limits**: Monitor memory and CPU usage

## Pre-PR Checks
```bash
# Run quality checks
pytest tests/ -v
black --check app/ tests/
isort --check-only app/ tests/
flake8 app/ tests/
mypy app/ --ignore-missing-imports
bandit -r app/ --exit-zero

# Test application startup
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 5
curl -f http://127.0.0.1:8000/ && echo "✅ App starts successfully"
pkill -f uvicorn
```