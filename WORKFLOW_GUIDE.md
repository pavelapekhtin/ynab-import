# Development and Release Workflow Guide

This document outlines the development workflow and release process for the YNAB Import Tool.

## 🌊 Branch Strategy

### Branch Structure
- **`main`** - Production-ready code, all releases are tagged from here
- **`staging`** - Integration branch for testing before release
- **`feature/*`** - Feature development branches

### Workflow Flow
```
feature/new-feature → staging → main → PyPI Release
```

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Create feature branch from staging
git checkout staging
git pull origin staging
git checkout -b feature/your-feature-name

# Develop your feature
# ... make changes ...

# Commit changes
git add .
git commit -m "feat: add new feature description"

# Push feature branch
git push origin feature/your-feature-name
```

### 2. Feature Integration
```bash
# Create PR: feature/your-feature → staging
# After review and CI passes, merge to staging
```

### 3. Release Preparation
```bash
# On staging branch, update version and changelog
cz bump --patch  # or --minor, --major

# Push changes
git push origin staging

# Create PR: staging → main
# This triggers comprehensive release validation
```

## 🚀 Release Process

### Automated Release Steps

1. **PR Validation** (staging → main)
   - Comprehensive test suite runs
   - Package building and validation
   - Version consistency checks
   - Changelog validation
   - Automatic PR comment with release readiness

2. **Merge to Main**
   - Only merge staging to main when ready for release
   - All automated checks must pass

3. **Tag Creation** (triggers PyPI release)
   ```bash
   git checkout main
   git pull origin main
   git tag v0.1.0  # Use actual version number
   git push origin v0.1.0
   ```

4. **Automated Publishing**
   - GitHub Actions builds package
   - Validates with twine
   - Creates GitHub release
   - Publishes to PyPI

## 📋 GitHub Actions Workflows

### CI Workflow (`.github/workflows/ci.yml`)
**Triggers:** Push to `main` or `staging`, PRs to `main` or `staging`

**Actions:**
- Cross-platform testing (Ubuntu, Windows, macOS)
- Python 3.12 testing
- Linting with ruff
- Type checking with pyright
- Test coverage reporting
- Package building validation

### Staging to Main Workflow (`.github/workflows/staging-to-main.yml`)
**Triggers:** PR from `staging` to `main`

**Actions:**
- Comprehensive test suite
- Package building and validation
- Version consistency verification
- Changelog validation
- Release readiness reporting

### Release Workflow (`.github/workflows/release.yml`)
**Triggers:** Tag push (v*) from `main` branch only

**Actions:**
- Verifies tag is from main branch
- Builds and validates package
- Creates GitHub release
- Publishes to PyPI

## 🔒 Branch Protection Rules

### Recommended GitHub Branch Protection (main)
```yaml
Protection Rules:
  - Require PR reviews: 1
  - Require status checks to pass
  - Require branches to be up to date
  - Required status checks:
    - CI / test (ubuntu-latest, 3.12)
    - CI / build
  - Restrict pushes to matching branches
  - Do not allow force pushes
  - Do not allow deletions
```

### Recommended GitHub Branch Protection (staging)
```yaml
Protection Rules:
  - Require status checks to pass
  - Required status checks:
    - CI / test (ubuntu-latest, 3.12)
  - Do not allow force pushes
```

## 🏷️ Version Management

### Using Commitizen
```bash
# Patch version (0.1.0 → 0.1.1) - bug fixes
cz bump --patch

# Minor version (0.1.0 → 0.2.0) - new features
cz bump --minor

# Major version (0.1.0 → 1.0.0) - breaking changes
cz bump --major

# Custom increment
cz bump --increment PATCH|MINOR|MAJOR
```

### Conventional Commits
Use conventional commit messages for automatic changelog generation:

```bash
git commit -m "feat: add support for new bank format"
git commit -m "fix: handle empty CSV files gracefully"
git commit -m "docs: update installation instructions"
git commit -m "test: add coverage for data converter"
git commit -m "refactor: simplify preset management"
```

## 🛡️ Release Safety

### Pre-Release Checklist
- [ ] All tests pass on staging branch
- [ ] Version bumped appropriately
- [ ] CHANGELOG.md updated with new changes
- [ ] README.md updated if needed
- [ ] Package builds without errors
- [ ] Manual testing completed

### Emergency Release Process
If urgent hotfix needed:
```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/urgent-fix

# Make minimal fix
# ... make changes ...

# Commit and push
git commit -m "fix: urgent security patch"
git push origin hotfix/urgent-fix

# Create PR: hotfix/urgent-fix → main
# After merge, immediately tag and release
git tag v0.1.1
git push origin v0.1.1

# Merge changes back to staging
git checkout staging
git merge main
git push origin staging
```

## 🔍 Troubleshooting

### Release Workflow Fails
1. Check that tag was created from main branch
2. Verify PyPI API token is configured in GitHub secrets
3. Ensure package builds locally: `uv build && twine check dist/*`

### CI Failures
1. Check test failures: `uv run pytest -v`
2. Check linting: `uv run ruff check .`
3. Check formatting: `uv run ruff format --check .`

### Version Conflicts
1. Ensure `pyproject.toml` and `__init__.py` versions match
2. Use `cz bump` to update versions consistently
3. Check that CHANGELOG.md has unreleased section

## 📞 Support

For workflow questions or issues:
- Check GitHub Actions logs
- Review this guide
- Create issue with `workflow` label