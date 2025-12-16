# Contributing to LLM User Management API

Thank you for your interest in contributing to the LLM User Management API! This document provides guidelines and best practices for contributing to this project.

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+
- Git
- GitHub CLI (optional, for enhanced GitHub integration)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/shamil2/llm_user_management.git
   cd llm_user_management
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create database**
   ```bash
    PYTHONPATH=. python scripts/create_tables.py
   ```

4. **Run tests**
   ```bash
   pytest tests/ -v
   ```

5. **Start development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📋 Development Workflow

### 1. Choose an Issue
- Check [GitHub Issues](https://github.com/shamil2/llm_user_management/issues) for open tasks
- Comment on the issue to indicate you're working on it

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes
- Write clean, well-documented code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 4. Run Quality Checks
```bash
# Run all quality checks
pytest tests/ -v
black --check app/ tests/
isort --check-only app/ tests/
flake8 app/ tests/
mypy app/ --ignore-missing-imports
bandit -r app/
```

### 5. Commit Changes
```bash
git add .
git commit -m "feat: add new feature description

- What was changed
- Why it was changed
- How it affects users"
```

Follow [Conventional Commits](https://conventionalcommits.org/) format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/updates
- `chore:` - Maintenance tasks

### 6. Create Pull Request
- Push your branch to GitHub
- Create a pull request with a clear description
- Reference any related issues
- Wait for CI checks to pass
- Request review from maintainers

## 🎯 Code Quality Standards

### Python Code Style
- **Black**: Code formatting (line length: 88 characters)
- **isort**: Import sorting
- **flake8**: Linting and style checking
- **mypy**: Type checking

### Testing
- **pytest**: Testing framework
- Minimum 80% code coverage required
- Tests should be colocated with the code they test
- Use descriptive test names and docstrings

### Security
- **bandit**: Security linting
- **safety**: Dependency vulnerability checking
- Never commit secrets or API keys
- Use environment variables for configuration
- Database files are excluded from version control

### Documentation
- Update README.md for significant changes
- Add docstrings to new functions/classes
- Update API documentation for endpoint changes
- Keep AGENTS.md files current for AI-assisted development

## 🔒 Security Considerations

### API Keys & Secrets
- Never commit API keys, passwords, or sensitive data
- Use `.env` files for local development
- Environment variables should have secure defaults
- Database files containing user data are excluded from git

### Authentication & Authorization
- JWT tokens should have reasonable expiration times
- API keys should be securely generated and stored
- Rate limiting should be implemented for production use
- Input validation on all endpoints

### Dependencies
- Keep dependencies updated and secure
- Use pinned versions in requirements.txt
- Regularly audit for vulnerabilities
- Minimize dependency footprint

## 🚀 Deployment

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
DATABASE_URL=sqlite:///./llm_users.db
JWT_SECRET_KEY=your-secure-secret-here
VLLM_ENDPOINT=http://localhost:8001
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] SSL/TLS enabled
- [ ] Rate limiting configured
- [ ] Logging set up
- [ ] Monitoring/alerting configured
- [ ] Backup strategy in place

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/shamil2/llm_user_management/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shamil2/llm_user_management/discussions)
- **Documentation**: Check the `docs/` folder and README.md

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

Thank you for contributing to the LLM User Management API! 🎉