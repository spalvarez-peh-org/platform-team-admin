"""
Unit tests for the GitHub rulesets module.

Tests the applyRepositoryRulesets function which creates GitHub branch protection rules
using Pulumi and pulumi-github provider.
"""

import pytest

from modules.github.rulesets import applyRepositoryRulesets


class TestApplyRepositoryRulesets:
    """Test cases for the applyRepositoryRulesets function."""

    def test_apply_rulesets_with_valid_inputs(self, patch_github_rulesets, assertions):
        """Test applying rulesets with valid repository and branch names."""
        mock_github = patch_github_rulesets

        result = applyRepositoryRulesets("test-repo", "main")

        # Use centralized assertion helper
        assertions.assert_branch_protection_called_with(
            mock_github, "test-repo-main-branch-protection", "test-repo", "main"
        )

        # Verify function returns the branch protection object
        assert result == mock_github.BranchProtection.return_value

    def test_apply_rulesets_with_different_branch(
        self, patch_github_rulesets, assertions
    ):
        """Test applying rulesets to a different branch."""
        mock_github = patch_github_rulesets

        result = applyRepositoryRulesets("my-repo", "develop")

        # Verify correct branch pattern
        assertions.assert_branch_protection_called_with(
            mock_github, "my-repo-develop-branch-protection", "my-repo", "develop"
        )

        assert result == mock_github.BranchProtection.return_value

    def test_enforce_admins_enabled(self, patch_github_rulesets):
        """Test that enforce_admins is always set to True."""
        mock_github = patch_github_rulesets

        applyRepositoryRulesets("repo", "branch")

        # Check that enforce_admins is True
        args, kwargs = mock_github.BranchProtection.call_args
        assert kwargs["enforce_admins"] is True

    def test_require_signed_commits_enabled(self, patch_github_rulesets):
        """Test that require_signed_commits is always set to True."""
        mock_github = patch_github_rulesets

        applyRepositoryRulesets("repo", "branch")

        # Check that require_signed_commits is True
        args, kwargs = mock_github.BranchProtection.call_args
        assert kwargs["require_signed_commits"] is True

    def test_resource_naming_patterns(
        self, patch_github_rulesets, ruleset_naming_patterns
    ):
        """Test resource naming with various repository and branch name patterns."""
        mock_github = patch_github_rulesets
        repo_name, branch_name, expected_resource_name = ruleset_naming_patterns

        applyRepositoryRulesets(repo_name, branch_name)

        # Verify resource name is constructed correctly
        args, kwargs = mock_github.BranchProtection.call_args
        actual_resource_name = args[0]
        assert actual_resource_name == expected_resource_name

    def test_repository_id_parameter(self, patch_github_rulesets):
        """Test that repository_id parameter is set correctly."""
        mock_github = patch_github_rulesets

        applyRepositoryRulesets("test-repository", "main")

        # Check repository_id parameter
        args, kwargs = mock_github.BranchProtection.call_args
        assert kwargs["repository_id"] == "test-repository"

    def test_pattern_parameter(self, patch_github_rulesets):
        """Test that pattern parameter matches the branch name."""
        mock_github = patch_github_rulesets

        applyRepositoryRulesets("repo", "feature/my-feature")

        # Check pattern parameter
        args, kwargs = mock_github.BranchProtection.call_args
        assert kwargs["pattern"] == "feature/my-feature"


@pytest.mark.integration
class TestApplyRepositoryRulesetsIntegration:
    """Integration tests for ruleset application workflow."""

    def test_multiple_rulesets_application(self, patch_github_rulesets):
        """Test applying rulesets to multiple repositories and branches."""
        mock_github = patch_github_rulesets

        test_cases = [
            ("repo1", "main"),
            ("repo2", "develop"),
            ("repo3", "feature/test"),
        ]

        results = []
        for repo_name, branch_name in test_cases:
            result = applyRepositoryRulesets(repo_name, branch_name)
            results.append(result)

        # Verify all rulesets were applied
        assert mock_github.BranchProtection.call_count == 3

        # Verify all results are the mock branch protection
        assert all(
            result == mock_github.BranchProtection.return_value for result in results
        )

    def test_ruleset_application_with_github_error(self, patch_github_rulesets):
        """Test handling of GitHub API errors during ruleset application."""
        mock_github = patch_github_rulesets

        # Simulate an error in BranchProtection creation
        mock_github.BranchProtection.side_effect = Exception("GitHub API Error")

        with pytest.raises(Exception, match="GitHub API Error"):
            applyRepositoryRulesets("error-repo", "main")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_none_inputs(self, patch_github_rulesets, assertions):
        """Test behavior when None values are passed."""
        mock_github = patch_github_rulesets

        result = applyRepositoryRulesets(None, None)

        # Verify function still works with None values
        assertions.assert_branch_protection_called_with(
            mock_github, "None-None-branch-protection", None, None
        )

        assert result == mock_github.BranchProtection.return_value

    def test_empty_string_inputs(self, patch_github_rulesets):
        """Test behavior with empty string inputs."""
        mock_github = patch_github_rulesets

        applyRepositoryRulesets("", "")

        # Verify function handles empty strings
        mock_github.BranchProtection.assert_called_once_with(
            "--branch-protection",
            repository_id="",
            pattern="",
            enforce_admins=True,
            require_signed_commits=True,
        )

    def test_special_characters_in_names(self, patch_github_rulesets):
        """Test behavior with special characters in repository and branch names."""
        mock_github = patch_github_rulesets

        applyRepositoryRulesets("repo-with-dashes", "feature/special@chars")

        # Verify special characters are preserved
        args, kwargs = mock_github.BranchProtection.call_args
        assert kwargs["repository_id"] == "repo-with-dashes"
        assert kwargs["pattern"] == "feature/special@chars"
        assert args[0] == "repo-with-dashes-feature/special@chars-branch-protection"


class TestWithFixtures:
    """Tests using pytest fixtures."""

    def test_with_standard_repo_data(
        self, patch_github_rulesets, standard_repo_branch_data, assertions
    ):
        """Test using standard repository fixture data."""
        mock_github = patch_github_rulesets

        result = applyRepositoryRulesets(
            standard_repo_branch_data["repo_name"],
            standard_repo_branch_data["branch_name"],
        )

        # Verify the call was made correctly using centralized assertion
        expected_resource_name = f"{standard_repo_branch_data['repo_name']}-{standard_repo_branch_data['branch_name']}-branch-protection"
        assertions.assert_branch_protection_called_with(
            mock_github,
            expected_resource_name,
            standard_repo_branch_data["repo_name"],
            standard_repo_branch_data["branch_name"],
        )

        assert result == mock_github.BranchProtection.return_value

    def test_with_feature_branch_data(
        self, patch_github_rulesets, feature_branch_data, assertions
    ):
        """Test using feature branch fixture data."""
        mock_github = patch_github_rulesets

        result = applyRepositoryRulesets(
            feature_branch_data["repo_name"], feature_branch_data["branch_name"]
        )

        # Verify feature branch handling using centralized assertion
        expected_resource_name = f"{feature_branch_data['repo_name']}-{feature_branch_data['branch_name']}-branch-protection"
        assertions.assert_branch_protection_called_with(
            mock_github,
            expected_resource_name,
            feature_branch_data["repo_name"],
            feature_branch_data["branch_name"],
        )

        assert result == mock_github.BranchProtection.return_value
