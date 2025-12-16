name: "Pull Request"

about: "Create a new pull request"

title: ""

labels: []

assignees: []

body: |
  ## Description
  <!-- Describe the changes made in this PR -->

  ## Type of Change
  - [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
  - [ ] ✨ New feature (non-breaking change which adds functionality)
  - [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
  - [ ] 📚 Documentation update
  - [ ] 🎨 Code style update (formatting, renaming)
  - [ ] ♻️ Refactor (no functional changes)
  - [ ] ⚡ Performance improvement
  - [ ] ✅ Test update
  - [ ] 🔧 Build/CI update
  - [ ] 🔒 Security update

  ## Testing
  - [ ] All tests pass (`pytest tests/ -v`)
  - [ ] Code formatting passes (`black --check app/ && isort --check-only app/`)
  - [ ] Linting passes (`flake8 app/`)
  - [ ] Type checking passes (`mypy app/ --ignore-missing-imports`)
  - [ ] Security checks pass (`bandit -r app/`)

  ## Security Considerations
  - [ ] No secrets or sensitive data committed
  - [ ] Database files excluded from version control
  - [ ] No hardcoded credentials or API keys

  ## Additional Notes
  <!-- Any additional information or context -->