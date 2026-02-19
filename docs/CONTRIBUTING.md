# Contributing to pybaiduphoto

Thank you for your interest in contributing to pybaiduphoto! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment (recommended)

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/baiduphoto.git
   cd baiduphoto
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix:
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # if available
   ```

5. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Development Workflow

### Branching Strategy

- `main` - Stable production code
- `develop` - Development branch for new features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Urgent production fixes

### Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards below

3. Test your changes thoroughly

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   See [Commit Message Guidelines](#commit-message-guidelines)

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for all public functions and classes

Example:
```python
def get_photos(self, limit: int = 100) -> List[OnlineItem]:
    """
    Get photos from the album.
    
    Args:
        limit: Maximum number of photos to retrieve
        
    Returns:
        List of OnlineItem objects
        
    Raises:
        ValueError: If limit is negative
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")
    # ...
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `OnlineItem`, `PersonAlbum`)
- **Functions/Methods**: snake_case (e.g., `get_photos`, `upload_file`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS`, `DEFAULT_PAGE_SIZE`)
- **Private methods**: single underscore prefix (e.g., `_getTID()`)

### Code Organization

- Keep functions focused and small
- Maximum function length: 50 lines
- Maximum cyclomatic complexity: 10
- Use meaningful variable names
- Avoid magic numbers - use named constants

### Comments and Documentation

- Write docstrings for all public APIs
- Use inline comments sparingly and only for complex logic
- Keep comments up to date with code changes
- Avoid commenting out code - remove it instead

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=pybaiduphoto
```

### Writing Tests

- Write unit tests for all new functions
- Aim for >80% code coverage
- Use descriptive test names
- Test both success and failure cases
- Use fixtures for common test data

Example:
```python
def test_get_album_by_id():
    """Test getting an album by ID."""
    # Arrange
    api = API(cookies=test_cookies)
    album_id = "test_album_id"
    
    # Act
    album = api.get_album_by_id(album_id)
    
    # Assert
    assert album is not None
    assert album.getID() == album_id
```

## Documentation

### Updating Documentation

- Keep README.md up to date with API changes
- Update ARCHITECTURE.md for structural changes
- Add examples for new features in `examples/` directory
- Update CHANGELOG.md for user-facing changes

### Writing Examples

Examples should:
- Be complete and runnable
- Include necessary imports
- Handle errors gracefully
- Include comments explaining key steps

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(upload): add support for batch upload

Implement batch upload functionality to upload multiple files
at once. This improves performance when uploading many files.

Closes #123
```

```
fix(album): resolve crash when deleting empty album

Fix null pointer exception when trying to delete an album
that has no items.

Fixes #456
```

## Pull Request Process

### Before Submitting

1. Ensure your code follows all coding standards
2. Run tests and ensure they pass
3. Update documentation if needed
4. Add your name to CONTRIBUTORS.md

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No new warnings
```

## Release Process

Releases are managed by maintainers:

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create git tag
4. Build and upload to PyPI

## Questions or Issues?

- Open an issue on GitHub
- Check existing documentation
- Search for similar issues

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).