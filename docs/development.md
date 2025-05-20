# Development Guide

## Development Setup

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/cptntrps/Mi7.git
cd Mi7
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
pip install -r ma_discussion/tests/requirements-test.txt
```

### IDE Configuration

#### VS Code
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.formatting.provider": "black"
}
```

#### PyCharm
- Enable pytest as test runner
- Set Black as code formatter
- Enable Pylint for linting

## Project Structure

```
Mi7/
├── docs/                    # Documentation
├── ma_discussion/          # Main package
│   ├── agents/            # Agent implementations
│   │   ├── base.py       # Base agent class
│   │   ├── coordinator.py # Coordinator agent
│   │   └── factory.py    # Agent factory
│   ├── services/         # External services
│   │   ├── ollama.py    # Ollama integration
│   │   ├── wikipedia.py # Wikipedia integration
│   │   └── settings.py  # Service settings
│   ├── ui/              # User interface
│   │   ├── main.py     # Main interface
│   │   ├── sidebar.py  # Sidebar interface
│   │   └── state.py    # App state management
│   ├── utils/           # Utilities
│   │   ├── json_io.py  # JSON utilities
│   │   └── regex.py    # Regex utilities
│   └── tests/           # Test files
├── agent_discussion_app.py  # Main entry point
├── requirements.txt         # Dependencies
└── pyproject.toml          # Project configuration
```

## Coding Standards

### Python Style Guide

1. Follow PEP 8 conventions
2. Use type hints for function arguments and returns
3. Write docstrings for all public functions and classes
4. Keep functions focused and under 50 lines
5. Use meaningful variable and function names

Example:
```python
from typing import Dict, Any, Optional

def process_response(
    response: str,
    context: Dict[str, Any],
    cleanup: bool = True
) -> Optional[Dict[str, Any]]:
    """Process an agent's response and extract structured data.
    
    Args:
        response: Raw response string from the agent
        context: Context dictionary for processing
        cleanup: Whether to clean up the response
        
    Returns:
        Processed response as a dictionary, or None if processing fails
        
    Raises:
        ValueError: If response is empty or invalid
    """
    if not response:
        raise ValueError("Empty response")
        
    # Processing logic here
    
    return processed_data
```

### Error Handling

1. Use specific exception types
2. Always log errors with context
3. Provide helpful error messages
4. Handle edge cases gracefully

Example:
```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Invalid data format: {str(e)}")
    return {"error": f"Data processing failed: {str(e)}"}
except Exception as e:
    logger.exception("Unexpected error in process_data")
    return {"error": "Internal processing error"}
```

### Testing

1. Write unit tests for all new code
2. Maintain test coverage above 80%
3. Use meaningful test names
4. Test edge cases and error conditions

Example:
```python
def test_process_response_with_valid_data():
    response = "Test response"
    context = {"key": "value"}
    result = process_response(response, context)
    assert result is not None
    assert "key" in result

def test_process_response_with_empty_input():
    with pytest.raises(ValueError):
        process_response("", {})
```

## Development Workflow

### 1. Feature Development

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Write code and tests:
```bash
# Write code
# Write tests
pytest ma_discussion/tests/
```

3. Check code quality:
```bash
pylint ma_discussion/
black ma_discussion/
```

4. Commit changes:
```bash
git add .
git commit -m "feat: Add your feature description"
```

### 2. Code Review Process

1. Push changes and create PR:
```bash
git push origin feature/your-feature-name
# Create PR on GitHub
```

2. PR Requirements:
- All tests passing
- Code coverage maintained
- Documentation updated
- Clean commit history

### 3. Release Process

1. Version bump:
```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
```

2. Create release:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Contributing Guidelines

### 1. Issue Reporting

- Use issue templates
- Provide clear reproduction steps
- Include relevant logs and screenshots
- Tag issues appropriately

### 2. Pull Requests

- Reference related issues
- Keep changes focused
- Update documentation
- Add tests for new features

### 3. Code Review

- Review within 2 business days
- Be constructive and respectful
- Focus on code, not the author
- Suggest improvements

## Debugging Tips

### 1. Logging

```python
import logging

logger = logging.getLogger(__name__)

def complex_operation():
    logger.debug("Starting operation")
    try:
        # Operation code
        logger.info("Operation successful")
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
```

### 2. Testing Tools

```bash
# Run specific test
pytest ma_discussion/tests/test_file.py::test_name

# Run with coverage
pytest --cov=ma_discussion

# Debug with pdb
pytest --pdb
```

### 3. Common Issues

1. JSON Parsing:
```python
try:
    data = json.loads(response)
except json.JSONDecodeError as e:
    logger.error(f"JSON parsing failed at position {e.pos}: {str(e)}")
```

2. API Connections:
```python
try:
    response = requests.post(url, timeout=30)
    response.raise_for_status()
except requests.Timeout:
    logger.error("API request timed out")
except requests.RequestException as e:
    logger.error(f"API request failed: {str(e)}")
```

## Performance Optimization

### 1. Memory Management

```python
def clear_history(self):
    """Clear conversation history to free memory."""
    self.conversation_history = []
    gc.collect()
```

### 2. Response Streaming

```python
def stream_response(self, prompt: str) -> Iterator[str]:
    """Stream response tokens for real-time feedback."""
    for token in self.ollama_service.stream_text(prompt):
        yield token
```

### 3. Caching

```python
@lru_cache(maxsize=100)
def get_wikipedia_summary(self, title: str) -> Optional[str]:
    """Cache Wikipedia summaries for frequent lookups."""
    return self.wikipedia_service.get_summary(title)
```

## Security Best Practices

### 1. Input Validation

```python
def validate_agent_config(config: Dict[str, Any]) -> bool:
    """Validate agent configuration input."""
    required = {"name", "role", "model"}
    return all(key in config for key in required)
```

### 2. Error Messages

```python
def handle_error(error: Exception) -> Dict[str, str]:
    """Create safe error messages for users."""
    if isinstance(error, ValueError):
        return {"error": str(error)}
    return {"error": "An internal error occurred"}
```

### 3. API Security

```python
def make_api_request(self, url: str, data: Dict[str, Any]) -> Response:
    """Make secure API requests."""
    headers = self._get_secure_headers()
    return requests.post(url, json=data, headers=headers, verify=True)
``` 