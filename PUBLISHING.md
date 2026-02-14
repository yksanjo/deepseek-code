# Publishing to PyPI | 发布到 PyPI

This guide explains how to publish DeepSeek Code to PyPI for easier installation.

本指南说明如何将 DeepSeek Code 发布到 PyPI 以便更轻松地安装。

---

## Why PyPI? | 为什么选择 PyPI?

- **Easier installation**: `pip install deepseek-code` instead of `pip install git+...`
- **Version management**: Semantic versioning with pip
- **Discovery**: Found by developers searching PyPI
- **Trust**: Official Python package index

---

## Prerequisites | 前置条件

1. Python 3.10+
2. PyPI account (https://pypi.org/account/register/)
3. Twine installed: `pip install twine build`

---

## Step-by-Step | 步骤指南

### 1. Prepare Your Package

Make sure your `pyproject.toml` is properly configured:

```toml
[project]
name = "deepseek-code"
version = "0.1.0"  # Update version for each release
description = "AI coding assistant powered by DeepSeek-V3"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = ["ai", "coding", "assistant", "deepseek", "cli"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "openai>=1.0.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "prompt-toolkit>=3.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
deepseek-code = "deepseek_code.cli:main"
dsc = "deepseek_code.cli:main"
```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/deepseek_code-0.1.0-py3-none-any.whl`
- `dist/deepseek_code-0.1.0.tar.gz`

### 3. Test on TestPyPI (Recommended)

```bash
# Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ deepseek-code
```

### 4. Upload to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*
```

### 5. Verify Installation

```bash
# Fresh install
pip install deepseek-code

# Test it works
deepseek-code --version
```

---

## Version Management | 版本管理

Follow Semantic Versioning (SemVer):

- **0.1.0** → 0.2.0 (new feature)
- **0.1.0** → 1.0.0 (breaking change)
- **0.1.0** → 0.1.1 (bug fix)

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` (create if not exists)
- [ ] Run tests: `pytest`
- [ ] Build package: `python -m build`
- [ ] Upload to TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Test installation from TestPyPI
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Tag release: `git tag v0.1.0 && git push --tags`

---

## Automated Publishing | 自动发布

### Using GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

### Get PyPI Token

1. Go to https://pypi.org/manage/account/
2. Click "Add API token"
3. Name: `github-actions`
4. Copy the token
5. Add to GitHub repo secrets as `PYPI_TOKEN`

---

## Installation After Publishing | 发布后的安装

Users can then install with:

```bash
# From PyPI
pip install deepseek-code

# With specific version
pip install deepseek-code==0.1.0

# Upgrade
pip install --upgrade deepseek-code
```

---

## Troubleshooting | 故障排除

### "File already exists"

```bash
# Increment version in pyproject.toml
# Rebuild and upload again
python -m build
twine upload dist/*
```

### "Invalid credentials"

```bash
# Use token authentication
twine upload --username __token__ --password YOUR_TOKEN dist/*
```

### "Package name already taken"

Choose a different name or contact PyPI administrators.

---

## Additional Resources | 额外资源

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Publishing Tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
