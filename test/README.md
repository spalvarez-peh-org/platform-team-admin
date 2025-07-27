# Testing Guide

This directory contains unit tests for the platform-team-admin project.

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
uv sync --group test
```

### Running All Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=modules --cov-report=html --cov-report=term

# Run only unit tests
uv run pytest -m unit

# Run only integration tests  
uv run pytest -m integration
```

### Running Specific Tests

```bash
# Run tests for a specific module
uv run pytest test/test_members.py

# Run a specific test class
uv run pytest test/test_members.py::TestAddPlatformTeamMember

# Run a specific test method
uv run pytest test/test_members.py::TestAddPlatformTeamMember::test_add_member_with_complete_info
```

## Test Structure

### Test Files

- `test_members.py` - Tests for the GitHub members module
- Add additional test files following the pattern `test_<module_name>.py`

### Test Categories

- **Unit Tests**: Test individual functions in isolation with mocked dependencies
- **Integration Tests**: Test interactions between multiple components
- **Edge Case Tests**: Test error conditions and boundary cases

## Test Data

The tests use pytest fixtures to provide consistent test data:

- `valid_member_complete` - Complete member information
- `valid_member_minimal` - Minimal member information
- `invalid_member_no_username` - Invalid member data for error testing

## Mocking Strategy

Tests use `unittest.mock` to mock:
- `pulumi_github.Membership` - GitHub API calls
- `pulumi.export` - Pulumi resource exports
- External dependencies

## Coverage

Coverage reports are generated in `htmlcov/` directory when using the `--cov-report=html` option.

Target coverage: 90%+

## Writing New Tests

1. Follow the existing naming convention: `test_<function_name>`
2. Use descriptive test names that explain what is being tested
3. Include docstrings explaining the test purpose
4. Use fixtures for common test data
5. Mock external dependencies
6. Test both happy path and error conditions

### Example Test Structure

```python
def test_function_name_with_valid_input(self):
    """Test that function works correctly with valid input."""
    # Arrange
    test_data = {...}
    
    # Act
    with patch('module.dependency') as mock_dep:
        result = function_under_test(test_data)
    
    # Assert
    mock_dep.assert_called_once_with(expected_args)
    assert result == expected_result
```
