# Contributing to AutoMesh

Thank you for your interest in contributing to AutoMesh! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

When filing a bug report, include:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **AutoMesh version** (`automesh --version`)
- **Operating system** and version
- **Python version** (if applicable)
- **Input files** (if possible, provide minimal test case)

### Suggesting Features

Feature suggestions are welcome! Please:
- Check the [Roadmap](docs/roadmap.md) first
- Search existing feature requests
- Provide clear use case and benefits
- Consider implementation complexity

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/karthikt/AutoMesh.git
   cd AutoMesh
   git checkout -b feature/your-feature-name
   ```

2. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements/dev.txt
   pip install -e .
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed
   - Keep commits atomic and well-described

4. **Run tests**
   ```bash
   pytest tests/
   ```

5. **Submit pull request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure CI passes

## Development Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) for Python code
- Use type hints where appropriate
- Write docstrings for public APIs
- Keep functions focused and modular

**Format code with Black:**
```bash
black src/ tests/
```

**Check with flake8:**
```bash
flake8 src/ tests/
```

### Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Use pytest fixtures for common setups
- Test edge cases and error conditions

**Run tests:**
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/unit/test_phase4_sdk.py

# With coverage
pytest --cov=meshmind tests/
```

### Documentation

- Update docstrings for API changes
- Add examples for new features
- Update README.md if needed
- Contribute to docs/ for major features

### Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Longer explanation if needed.

Fixes #123
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
- `feat(detection): add GPU-accelerated FPFH computation`
- `fix(export): handle missing MRF zones gracefully`
- `docs(readme): update installation instructions`

## Project Structure

```
AutoMesh/
├── src/meshmind/          # Main package
│   ├── io/                # File I/O
│   ├── core/              # Core algorithms
│   ├── cfd/               # CFD integration
│   └── sdk/               # Public API
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
└── scripts/               # Utility scripts
```

## Building Documentation

```bash
cd docs
python -m http.server 8000
# Open http://localhost:8000
```

## Release Process

Maintainers follow this process for releases:

1. Update version in `src/meshmind/_version.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v1.x.x -m "Release v1.x.x"`
4. Push tag: `git push origin v1.x.x`
5. GitHub Actions builds and publishes release

## Getting Help

- 📖 Read the [documentation](https://karthikt.github.io/AutoMesh)
- 💬 Open a [discussion](https://github.com/karthikt/AutoMesh/discussions)
- 🐛 File an [issue](https://github.com/karthikt/AutoMesh/issues)

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- CHANGELOG.md
- Release notes

Thank you for making AutoMesh better! 🙏
