"""
Unit tests for the GitHub repos module.

Tests the createRepository function which creates GitHub repositories
using Pulumi and pulumi-github provider.
"""

import pytest

from modules.github.repos import createRepository


class TestCreateRepository:
    """Test cases for the createRepository function."""

    def test_create_repository_with_complete_info(
        self, patch_github_repos, valid_repo_data, assertions
    ):
        """Test creating a repository with name and description."""
        mock_pulumi, mock_github = patch_github_repos

        result = createRepository(
            valid_repo_data["name"], valid_repo_data["description"]
        )

        # Use centralized assertion helper
        assertions.assert_repository_called_with(
            mock_github,
            mock_pulumi,
            valid_repo_data["name"],
            valid_repo_data["description"],
        )

        # Verify pulumi export was called
        assertions.assert_pulumi_export_called_with(
            mock_pulumi,
            f"{valid_repo_data['name']}-repository",
            mock_github.Repository.return_value.name,
        )

        # Verify ResourceOptions was called with protect=True
        mock_pulumi.ResourceOptions.assert_called_once_with(protect=True)

        # Verify function returns the repository object
        assert result == mock_github.Repository.return_value

    def test_create_repository_with_empty_description(
        self, patch_github_repos, assertions
    ):
        """Test creating a repository with empty description."""
        mock_pulumi, mock_github = patch_github_repos

        createRepository("repo-no-desc", "")

        # Verify repository was created with empty description
        assertions.assert_repository_called_with(
            mock_github, mock_pulumi, "repo-no-desc", ""
        )

    def test_create_repository_protection_enabled(self, patch_github_repos):
        """Test that repository is created with protection enabled."""
        mock_pulumi, mock_github = patch_github_repos

        createRepository("protected-repo", "Protected repository")

        # Verify ResourceOptions called with protect=True
        mock_pulumi.ResourceOptions.assert_called_once_with(protect=True)

    def test_create_repository_public_visibility(self, patch_github_repos):
        """Test that repository is created with public visibility."""
        mock_pulumi, mock_github = patch_github_repos

        createRepository("public-repo", "Public repository")

        # Check that visibility is set to public
        args, kwargs = mock_github.Repository.call_args
        assert kwargs["visibility"] == "public"

    def test_create_repository_various_names(
        self, patch_github_repos, repo_name_patterns, assertions
    ):
        """Test creating repositories with various naming patterns."""
        mock_pulumi, mock_github = patch_github_repos
        repo_name, description = repo_name_patterns

        createRepository(repo_name, description)

        # Verify correct parameters
        assertions.assert_repository_called_with(
            mock_github, mock_pulumi, repo_name, description
        )

        # Verify export name format
        expected_export = f"{repo_name}-repository"
        assertions.assert_pulumi_export_called_with(
            mock_pulumi, expected_export, mock_github.Repository.return_value.name
        )


@pytest.mark.integration
class TestCreateRepositoryIntegration:
    """Integration tests for repository creation workflow."""

    def test_multiple_repositories_workflow(self, patch_github_repos):
        """Test creating multiple repositories in sequence."""
        mock_pulumi, mock_github = patch_github_repos

        repositories = [
            ("repo1", "First repository"),
            ("repo2", "Second repository"),
            ("repo3", "Third repository"),
        ]

        results = []
        for repo_name, description in repositories:
            result = createRepository(repo_name, description)
            results.append(result)

        # Verify all repositories were created
        assert mock_github.Repository.call_count == 3
        assert mock_pulumi.export.call_count == 3
        assert mock_pulumi.ResourceOptions.call_count == 3

        # Verify all results are the mock repository
        assert all(result == mock_github.Repository.return_value for result in results)

    def test_repository_creation_with_pulumi_error(self, patch_github_repos):
        """Test handling of Pulumi errors during repository creation."""
        mock_pulumi, mock_github = patch_github_repos

        # Simulate an error in GitHub Repository creation
        mock_github.Repository.side_effect = Exception("GitHub API Error")

        with pytest.raises(Exception, match="GitHub API Error"):
            createRepository("error-repo", "This will fail")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_none_inputs(self, patch_github_repos, assertions):
        """Test behavior when None values are passed."""
        mock_pulumi, mock_github = patch_github_repos

        result = createRepository(None, None)

        # Verify function still works with None values
        # Note: f"{None}" becomes "None" string in the actual implementation
        mock_github.Repository.assert_called_once_with(
            "None",  # f"{None}" converts to string "None"
            name=None,
            description=None,
            visibility="public",
            opts=mock_pulumi.ResourceOptions.return_value,
        )

        assert result == mock_github.Repository.return_value

    def test_empty_string_inputs(self, patch_github_repos):
        """Test behavior with empty string inputs."""
        mock_pulumi, mock_github = patch_github_repos

        createRepository("", "")

        # Verify function handles empty strings
        mock_github.Repository.assert_called_once_with(
            "",
            name="",
            description="",
            visibility="public",
            opts=mock_pulumi.ResourceOptions.return_value,
        )

    def test_with_fixture_data(self, patch_github_repos, valid_repo_data, assertions):
        """Test using pytest fixture data."""
        mock_pulumi, mock_github = patch_github_repos

        result = createRepository(
            valid_repo_data["name"], valid_repo_data["description"]
        )

        # Verify the call was made correctly using centralized assertion
        assertions.assert_repository_called_with(
            mock_github,
            mock_pulumi,
            valid_repo_data["name"],
            valid_repo_data["description"],
        )

        assert result == mock_github.Repository.return_value
