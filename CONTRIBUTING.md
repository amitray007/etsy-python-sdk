# Contributing to Etsy Python SDK

Thank you for your interest in contributing to the Etsy Python SDK! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct: be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Issues

- Check if the issue already exists in [GitHub Issues](https://github.com/amitray007/etsy-python-sdk/issues)
- Provide a clear description of the issue
- Include steps to reproduce the problem
- Share relevant code snippets or error messages
- Specify your Python version and OS

### Suggesting Features

- Open an issue with the `enhancement` label
- Clearly describe the feature and its use case
- Provide examples of how it would work

### Submitting Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/etsy-python-sdk.git
   cd etsy-python-sdk
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   pip install -r etsy_python/requirements.txt
   ```

4. **Make Your Changes**
   - Follow the existing code style
   - Add type hints to all functions
   - Update documentation as needed
   - Ensure version consistency

5. **Test Your Changes**
   ```bash
   # Check version consistency
   python scripts/check_version_consistency.py
   
   # Test imports
   python -c "from etsy_python._version import __version__; print(__version__)"
   ```

6. **Commit Your Changes**
   
   Use semantic commit messages for automatic versioning:
   
   - `fix:` - Bug fixes (triggers patch version bump)
   - `feat:` - New features (triggers minor version bump)
   - `breaking:` or `BREAKING CHANGE:` - Breaking changes (triggers major version bump)
   - `docs:` - Documentation updates
   - `chore:` - Maintenance tasks
   - `test:` - Test additions or fixes
   
   Examples:
   ```bash
   git commit -m "fix: correct OAuth token refresh timing"
   git commit -m "feat: add support for new Etsy API endpoints"
   git commit -m "breaking: remove deprecated v2 API support"
   ```
   
   **Skipping CI/CD:** To make changes without triggering automatic versioning and deployment, add `[skip ci]` to your commit message:
   ```bash
   git commit -m "docs: update README [skip ci]"
   git commit -m "chore: fix typo in comments [skip ci]"
   ```

7. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a PR on GitHub.

## Development Guidelines

### Code Style

- **PEP 8 compliance** - Follow Python style guidelines
- **Type hints** - Use type annotations for all functions
- **Docstrings** - Document all public methods and classes
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Enums: `PascalCase` class, `UPPER_SNAKE_CASE` values

### Project Structure

When adding new features:

1. **Models** (`etsy_python/v3/models/`) - Request/response data structures
2. **Resources** (`etsy_python/v3/resources/`) - API endpoint implementations
3. **Enums** (`etsy_python/v3/enums/`) - Type-safe constants
4. **Exceptions** (`etsy_python/v3/exceptions/`) - Custom error classes

### Adding New API Endpoints

1. Create or update the request model:
   ```python
   # etsy_python/v3/models/YourFeature.py
   class YourFeatureRequest(Request):
       nullable = ["optional_field"]
       mandatory = ["required_field"]
       
       def __init__(self, required_field, optional_field=None):
           self.required_field = required_field
           self.optional_field = optional_field
           super().__init__(nullable=self.nullable, mandatory=self.mandatory)
   ```

2. Add enum if needed:
   ```python
   # etsy_python/v3/enums/YourFeature.py
   class YourFeatureType(Enum):
       TYPE_A = "type_a"
       TYPE_B = "type_b"
   ```

3. Implement the resource method:
   ```python
   # etsy_python/v3/resources/YourFeature.py
   @dataclass
   class YourFeatureResource:
       session: EtsyClient
       
       def your_method(self, param: int, request: YourFeatureRequest):
           endpoint = f"/endpoint/{param}"
           return self.session.make_request(endpoint, method=Method.POST, payload=request)
   ```

### Testing

While there's no formal test framework, ensure:
- Your code imports successfully
- Version consistency is maintained
- Example usage works as expected

### Documentation

- Update README.md with usage examples for new features
- Add docstrings to all new methods
- Update CHANGELOG.md if you create one

## Release Process

Releases are automated when changes are merged to `master`:

1. **Automatic Version Bump** - Based on commit messages
2. **Package Build** - Creates distribution files
3. **PyPI Publish** - Uploads to Python Package Index
4. **GitHub Release** - Creates release with changelog

### Manual Testing Release

For maintainers testing releases locally:

```bash
# Test version bump without pushing
python scripts/bump_version.py --dry-run --type patch

# Create local release without pushing
python scripts/release.py patch --no-push --no-build
```

## Questions?

If you have questions, please:
1. Check the [documentation](README.md)
2. Search existing [issues](https://github.com/amitray007/etsy-python-sdk/issues)
3. Open a new issue with your question

Thank you for contributing to the Etsy Python SDK!