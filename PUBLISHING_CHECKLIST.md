# PyPI Publishing Checklist

This checklist covers the steps to publish your YNAB Import Tool to PyPI.

## ✅ Pre-Publication Setup (COMPLETED)

- [x] Enhanced `pyproject.toml` with comprehensive metadata
- [x] Added MIT License file
- [x] Created comprehensive README.md with badges and examples
- [x] Added CHANGELOG.md following Keep a Changelog format
- [x] Set up proper package versioning with commitizen
- [x] Added `__init__.py` with version information
- [x] Created GitHub issue and PR templates
- [x] Set up CI/CD workflows for testing and releases
- [x] Configured package building and exclusions
- [x] Validated package with twine check

## 📝 Before Publishing (TODO)

### 1. ✅ Personal Information Updated
Author information has been set to Pavel Apekhtin (pavelapekdev@gmail.com)

### 2. ✅ GitHub URLs Updated
All URLs have been updated to use `pavelapekhtin` GitHub username

### 3. Create GitHub Repository
1. Create repository on GitHub
2. Push your code:
   ```bash
   git remote add origin https://github.com/pavelapekhtin/ynab-import.git
   git push -u origin main
   ```

### 4. Set Up PyPI Account
1. Create account at https://pypi.org/
2. Generate API token at https://pypi.org/manage/account/token/
3. Store token securely for GitHub Actions

## 🚀 Publishing Steps

### Automated Release Process (Recommended)

#### Prerequisites
1. Set up PyPI API token as GitHub secret `PYPI_API_TOKEN`
2. Configure branch protection rules (see `WORKFLOW_GUIDE.md`)

#### Release Steps
1. **Develop on staging branch:**
   ```bash
   git checkout staging
   # Make your changes...
   cz bump --patch  # or --minor/--major
   git push origin staging
   ```

2. **Create staging → main PR:**
   - PR will trigger comprehensive validation
   - Automated comment will confirm release readiness

3. **Merge to main and tag:**
   ```bash
   git checkout main
   git pull origin main
   git tag v0.1.0  # Use actual version from pyproject.toml
   git push origin v0.1.0
   ```

4. **Automated publishing:**
   - GitHub Actions will build and publish to PyPI
   - GitHub release will be created automatically

### Manual Publishing (Fallback)
```bash
# Build the package
uv build

# Check the package
twine check dist/*

# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ ynab-import

# Upload to PyPI
twine upload dist/*
```

## 🔄 Version Management

Use commitizen for version bumping:
```bash
# Patch version (0.1.0 -> 0.1.1)
cz bump --patch

# Minor version (0.1.0 -> 0.2.0)
cz bump --minor

# Major version (0.1.0 -> 1.0.0)
cz bump --major
```

## 📋 Post-Publication

- [ ] Test installation: `pip install ynab-import`
- [ ] Verify CLI works: `ynab-import`
- [ ] Update documentation with installation instructions
- [ ] Create GitHub release with release notes
- [ ] Share on relevant communities (Reddit, Discord, etc.)

## 🔧 Package Structure Summary

```
ynab-import/
├── src/ynab_import/          # Main package code
├── tests/                    # Test suite
├── .github/                  # GitHub templates and workflows
├── pyproject.toml           # Package configuration
├── README.md                # Package documentation
├── LICENSE                  # MIT License
├── CHANGELOG.md             # Version history
├── MANIFEST.in              # Package inclusion rules
└── dist/                    # Built packages (created by uv build)
```

## 🎯 Current Status

✅ **Package is ready for publication!**

The package builds successfully, passes all validation checks, and includes all necessary metadata for PyPI publication. Only personal information and GitHub URLs need to be updated before publishing.
