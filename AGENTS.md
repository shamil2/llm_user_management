# LLM User Management API - AGENTS.md

## Project Snapshot
- **Type**: Simple single Python project
- **Stack**: Python 3.9+, FastAPI, vLLM, SQLAlchemy, JWT auth
- **Purpose**: API proxy for vLLM with user authentication and token usage tracking
- Sub-packages have their own AGENTS.md files for detailed guidance

## Root Setup Commands
- Install: `pip install -r requirements.txt`
- Dev server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Build: `pip install --upgrade -r requirements.txt` (no build step for Python)
- Typecheck: `mypy app/ --ignore-missing-imports`
- Test all: `pytest tests/ -v`

## Universal Conventions
- Code style: Black formatter, isort imports, flake8 linting
- Commit format: Conventional commits (`feat:`, `fix:`, `docs:`)
- Branch strategy: `main` for production, feature branches for development
- PR requirements: Tests pass, typecheck passes, code reviewed

## Security & Secrets
- Never commit API keys, JWT secrets, or database credentials
- Use `.env` files for secrets (copy from `.env.example`)
- JWT tokens expire in 24h, refresh via `/auth/refresh` endpoint

## JIT Index - Directory Map

### Package Structure
- Main API: `app/` → [see app/AGENTS.md](app/AGENTS.md)
- OpenAI Provider: `opencode_provider_flask.py` → OpenAI-compatible API for OpenCode integration
- Tests: `tests/` → Integration tests with pytest fixtures
- Scripts: `scripts/` → Database setup and migrations

### Quick Find Commands
- Find API routes: `grep -rn "def " app/routers/ | grep -E "(get|post|put|delete)"`
- Find models: `grep -rn "class.*Base" app/models/`
- Find middleware: `grep -rn "class.*Middleware" app/`
- Find tests: `find . -name "*.py" -path "./tests/*" -exec grep -l "def test_" {} \;`

## CI/CD Pipeline

### Automated Quality Gates (`.github/workflows/ci.yml`)
All pull requests and pushes are automatically validated with these checks:

1. **Multi-Python Testing** - Runs on Python 3.9, 3.10, 3.11
   - Unit tests with pytest
   - Coverage reporting with Codecov
   - Database integration tests

2. **Code Quality Checks**
   - **Black**: Code formatting validation
   - **isort**: Import sorting validation
   - **flake8**: Linting and style checking
   - **mypy**: Type checking

3. **Security Scanning**
   - **Bandit**: Python security linting
   - Secrets detection in code

4. **Application Validation**
   - Server startup testing
   - API endpoint validation
   - OpenAPI schema generation

5. **Dependency Analysis**
   - Requirements.txt format validation

### ⚠️ CRITICAL: Never Merge Failing CI

**BEFORE MERGING ANY PR**:
```bash
# Check CI status
gh run list --limit 5

# View detailed CI results
gh run view <run-id> --log

# If ANY checks fail:
# 1. DO NOT MERGE
# 2. Fix the failing check
# 3. Push the fix
# 4. Wait for CI to pass
# 5. THEN merge
```

## Development Workflow

### Pre-Commit Quality Checks
```bash
# Run all quality checks locally before committing
pytest tests/ -v
black --check app/ tests/ scripts/
isort --check-only app/ tests/ scripts/
flake8 app/ tests/ scripts/
mypy app/ --ignore-missing-imports
bandit -r app/ --exit-zero
```

### Branch Strategy
- `main` - Production branch (protected)
- `feature/*` - New features
- `fix/*` - Bug fixes
- `chore/*` - Maintenance tasks

### Commit Message Format
Follow [Conventional Commits](https://conventionalcommits.org/):
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `style:` - Code formatting
- `refactor:` - Code changes
- `test:` - Test additions
- `chore:` - Maintenance

## Definition of Done
- All CI checks pass (test, lint, security, build, dependencies)
- Code coverage maintained
- No security vulnerabilities
- API documentation up to date
- Manual testing of critical paths
- PR approved and merged
