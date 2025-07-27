"""
Shared pytest configuration and fixtures for all tests.

This file provides common test infrastructure, fixtures, and utilities
used across all test modules in the platform-team-admin project.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the modules directory to the Python path for importing
# This ensures all test files can import modules without path manipulation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ============================================================================
# SHARED FIXTURES FOR MOCKING PULUMI COMPONENTS
# ============================================================================


@pytest.fixture
def mock_pulumi():
    """Mock the pulumi module with common methods."""
    mock = Mock()
    mock.export = Mock()
    mock.ResourceOptions = Mock()
    mock.ResourceOptions.return_value = Mock()
    return mock


@pytest.fixture
def mock_github():
    """Mock the pulumi_github module with common classes."""
    mock = Mock()

    # Mock Membership class
    mock.Membership = Mock()
    mock_membership = Mock()
    mock_membership.username = "test-username"
    mock.Membership.return_value = mock_membership

    # Mock Repository class
    mock.Repository = Mock()
    mock_repository = Mock()
    mock_repository.name = "test-repo"
    mock.Repository.return_value = mock_repository

    # Mock BranchProtection class
    mock.BranchProtection = Mock()
    mock_branch_protection = Mock()
    mock.BranchProtection.return_value = mock_branch_protection

    return mock


@pytest.fixture
def mock_membership():
    """Mock a GitHub membership object."""
    mock = Mock()
    mock.username = "test-username"
    return mock


@pytest.fixture
def mock_repository():
    """Mock a GitHub repository object."""
    mock = Mock()
    mock.name = "test-repository"
    return mock


@pytest.fixture
def mock_branch_protection():
    """Mock a GitHub branch protection object."""
    mock = Mock()
    return mock


# ============================================================================
# CONTEXT MANAGER FIXTURES FOR PATCHING
# ============================================================================


@pytest.fixture
def patch_github_members(mock_pulumi, mock_github):
    """Context manager for patching GitHub members module dependencies."""
    with (
        patch("modules.github.members.pulumi", mock_pulumi),
        patch("modules.github.members.github", mock_github),
    ):
        yield mock_pulumi, mock_github


@pytest.fixture
def patch_github_repos(mock_pulumi, mock_github):
    """Context manager for patching GitHub repos module dependencies."""
    with (
        patch("modules.github.repos.pulumi", mock_pulumi),
        patch("modules.github.repos.github", mock_github),
    ):
        yield mock_pulumi, mock_github


@pytest.fixture
def patch_github_rulesets(mock_github):
    """Context manager for patching GitHub rulesets module dependencies."""
    with patch("modules.github.rulesets.github", mock_github):
        yield mock_github


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def valid_member_complete():
    """Fixture providing complete member information."""
    return {"name": "John Doe", "github-username": "johndoe", "github-role": "admin"}


@pytest.fixture
def valid_member_minimal():
    """Fixture providing minimal member information."""
    return {"name": "Jane Smith", "github-username": "janesmith"}


@pytest.fixture
def invalid_member_no_username():
    """Fixture providing member info without username."""
    return {"name": "No Username User", "github-role": "member"}


@pytest.fixture
def valid_repo_data():
    """Fixture providing valid repository data."""
    return {
        "name": "test-repository",
        "description": "A test repository for unit testing",
    }


@pytest.fixture
def minimal_repo_data():
    """Fixture providing minimal repository data."""
    return {"name": "minimal-repo", "description": ""}


@pytest.fixture
def standard_repo_branch_data():
    """Fixture providing standard repository and branch data."""
    return {"repo_name": "standard-repository", "branch_name": "main"}


@pytest.fixture
def feature_branch_data():
    """Fixture providing feature branch data."""
    return {"repo_name": "feature-repo", "branch_name": "feature/new-feature"}


# ============================================================================
# PARAMETRIZED TEST DATA
# ============================================================================


@pytest.fixture(
    params=[
        ("member", "member"),
        ("admin", "admin"),
        ("maintainer", "maintainer"),
    ]
)
def github_roles(request):
    """Parametrized fixture for different GitHub roles."""
    return request.param


@pytest.fixture(
    params=[
        ("simple-repo", "Simple repository"),
        ("complex-repo-name", "Complex repository with longer description"),
        ("repo_with_underscores", "Repository with underscores"),
        ("UPPER-CASE-REPO", "Repository with uppercase letters"),
        ("123-numeric-repo", "Repository starting with numbers"),
    ]
)
def repo_name_patterns(request):
    """Parametrized fixture for various repository naming patterns."""
    return request.param


@pytest.fixture(
    params=[
        ("simple-repo", "main", "simple-repo-main-branch-protection"),
        ("complex-repo-name", "develop", "complex-repo-name-develop-branch-protection"),
        (
            "repo_with_underscores",
            "feature/test",
            "repo_with_underscores-feature/test-branch-protection",
        ),
        ("UPPER-CASE", "UPPER-BRANCH", "UPPER-CASE-UPPER-BRANCH-branch-protection"),
        ("123-numeric", "v1.0", "123-numeric-v1.0-branch-protection"),
    ]
)
def ruleset_naming_patterns(request):
    """Parametrized fixture for ruleset resource naming patterns."""
    return request.param


# ============================================================================
# UTILITY FIXTURES AND HELPERS
# ============================================================================


@pytest.fixture
def empty_dict():
    """Fixture providing an empty dictionary."""
    return {}


@pytest.fixture
def none_values():
    """Fixture providing None values for testing edge cases."""
    return None


@pytest.fixture
def empty_string():
    """Fixture providing empty string for testing edge cases."""
    return ""


# ============================================================================
# ASSERTION HELPERS
# ============================================================================


class AssertionHelpers:
    """Helper class with common assertion patterns."""

    @staticmethod
    def assert_membership_called_with(
        mock_github, expected_resource_name, expected_username, expected_role
    ):
        """Assert that GitHub Membership was called with expected parameters."""
        mock_github.Membership.assert_called_once_with(
            expected_resource_name, username=expected_username, role=expected_role
        )

    @staticmethod
    def assert_repository_called_with(
        mock_github, mock_pulumi, expected_name, expected_description
    ):
        """Assert that GitHub Repository was called with expected parameters."""
        mock_github.Repository.assert_called_once_with(
            expected_name,
            name=expected_name,
            description=expected_description,
            visibility="public",
            opts=mock_pulumi.ResourceOptions.return_value,
        )

    @staticmethod
    def assert_branch_protection_called_with(
        mock_github, expected_resource_name, expected_repo_id, expected_pattern
    ):
        """Assert that GitHub BranchProtection was called with expected parameters."""
        mock_github.BranchProtection.assert_called_once_with(
            expected_resource_name,
            repository_id=expected_repo_id,
            pattern=expected_pattern,
            enforce_admins=True,
            require_signed_commits=True,
        )

    @staticmethod
    def assert_pulumi_export_called_with(
        mock_pulumi, expected_export_name, expected_value
    ):
        """Assert that pulumi.export was called with expected parameters."""
        mock_pulumi.export.assert_called_once_with(expected_export_name, expected_value)


@pytest.fixture
def assertions():
    """Fixture providing assertion helper methods."""
    return AssertionHelpers()


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# ============================================================================
# TEST SESSION FIXTURES
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Set up test session with common configuration."""
    # Disable Pulumi output during tests
    os.environ["PULUMI_SKIP_UPDATE_CHECK"] = "true"
    os.environ["PULUMI_CONFIG_PASSPHRASE"] = "test"

    yield

    # Cleanup after tests
    if "PULUMI_SKIP_UPDATE_CHECK" in os.environ:
        del os.environ["PULUMI_SKIP_UPDATE_CHECK"]
    if "PULUMI_CONFIG_PASSPHRASE" in os.environ:
        del os.environ["PULUMI_CONFIG_PASSPHRASE"]
