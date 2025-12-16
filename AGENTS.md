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

## Definition of Done
- All tests pass (`pytest tests/`)
- Typecheck passes (`mypy app/`)
- API documentation generated (`fastapi dev app/main.py --docs`)
- Manual test of auth flow and token counting


## CI/CD Checks - MUST PASS BEFORE MERGE

### Automated PR Checks (`.github/workflows/pr-checklist.yml`)
All pull requests are automatically validated with these checks:

1. **PR Title Format** - MUST start with `feat:`, `feature:`, `fix:`, `chore:`, or `docs:`
   - ❌ Failure example: "Add feature" (missing prefix)
   - ✅ Success example: "feat: Add backup automation" or "feature: Add backup automation"

2. **Branch Naming** - MUST start with `feature/`, `feat/`, `fix/`, `chore/`, `docs/`, `security/`, `monitoring/`, or `operations/`
   - ❌ Failure example: `bugfix/fix-error` (use `fix/` not `bugfix/`)
   - ✅ Success example: `feature/backup-automation`, `security/network-policies`

3. **YAML File Extensions** - MUST use `.yml` NOT `.yaml`
   - ❌ Failure: Any file with `.yaml` extension
   - ✅ Success: All YAML files use `.yml`

4. **Encrypted Secrets** - All secrets MUST be SOPS-encrypted
   - ❌ Failure: Plain text secrets in repository
   - ✅ Success: All secrets in `.enc.yml` files

5. **Directory Structure** - Services MUST have `README.md`
   - ❌ Failure: `services/myservice/` without README.md
   - ✅ Success: All service directories have README.md

### ⚠️ CRITICAL: Never Merge Failing PRs

**BEFORE MERGING ANY PR**:
```bash
# Check PR status
gh pr view <pr-number>

# View check status
gh pr checks <pr-number>

# If ANY checks fail:
# 1. DO NOT MERGE
# 2. Fix the failing check
# 3. Push the fix
# 4. Wait for checks to pass
# 5. THEN merge
```


**Common Failures and Fixes**:

| Failure                  | Fix                                                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| PR title check failed    | Change title to start with `feat:`, `feature:`, `fix:`, `chore:`, or `docs:`                                                   |
| Branch naming failed     | Rename branch to accepted prefix: `feature/`, `feat/`, `fix/`, `chore/`, `docs/`, `security/`, `monitoring/`, or `operations/` |
| Encrypted secrets failed | Ensure all secrets use `.enc.yml` and are SOPS-encrypted                                                                       |
| README missing           | Add `README.md` to service directory                                                                                           |

## Validation Checklist

Before committing changes:
- [ ] All secrets SOPS-encrypted (`.enc.yml`)
- [ ] No hardcoded passwords
- [ ] README.md updated if needed
- [ ] AGENTS.md and CLAUDE.md are updated to take into account requirements asked that makes sense
- [ ] No unencrypted secrets committed
- [ ] `.sops/key.txt` NOT committed
- [ ] **MANDATORY**: Do not commit to main. Use pull request strategy

Before deploying:
- [ ] SOPS key available: `export SOPS_AGE_KEY_FILE=.sops/key.txt`
- [ ] Dry run completed successfully
- [ ] Backup taken if making destructive changes
- [ ] Secrets deployed
