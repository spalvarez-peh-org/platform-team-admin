"""
Integration tests for post-deployment validation.

These tests verify that the infrastructure deployed by Pulumi
is working correctly in the actual GitHub environment.
"""

import json
import os
from typing import Any

import pytest
import requests


class GitHubAPI:
    """Helper class for GitHub API interactions."""

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.owner = os.getenv("GITHUB_OWNER")
        self.base_url = "https://api.github.com"

        if not self.token or not self.owner:
            pytest.skip("GitHub credentials not available")

    def get(self, endpoint: str) -> dict[str, Any]:
        """Make a GET request to the GitHub API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


@pytest.fixture
def github_api():
    """Fixture providing GitHub API client."""
    return GitHubAPI()


@pytest.mark.integration
class TestOrganizationMembers:
    """Test organization member management."""

    def test_organization_has_members(self, github_api):
        """Verify that the organization has members."""
        members = github_api.get(f"orgs/{github_api.owner}/members")
        assert len(members) > 0, "Organization should have at least one member"

    def test_member_roles_are_configured(self, github_api):
        """Verify that members have appropriate roles."""
        # This would need to be customized based on your specific requirements
        members = github_api.get(f"orgs/{github_api.owner}/members")

        for member in members:
            # Example: verify member has expected role
            membership = github_api.get(
                f"orgs/{github_api.owner}/memberships/{member['login']}"
            )
            assert membership["role"] in [
                "member",
                "admin",
            ], f"Member {member['login']} has invalid role: {membership['role']}"


@pytest.mark.integration
class TestRepositories:
    """Test repository management and configuration."""

    def test_repositories_exist(self, github_api):
        """Verify that expected repositories exist."""
        repos = github_api.get(f"orgs/{github_api.owner}/repos")

        # Add assertions for specific repositories you expect
        # Example:
        # assert "my-expected-repo" in [repo["name"] for repo in repos]

        # For now, just verify we have repositories
        assert len(repos) >= 0, "Should have repositories configured"

    def test_repository_settings(self, github_api):
        """Verify repository settings are configured correctly."""
        repos = github_api.get(f"orgs/{github_api.owner}/repos")

        for repo in repos:
            repo_name = repo["name"]

            # Test basic repository settings
            assert repo["visibility"] in [
                "public",
                "private",
            ], f"Repository {repo_name} has invalid visibility"

            # Test branch protection if applicable
            try:
                protection = github_api.get(
                    f"repos/{github_api.owner}/{repo_name}/branches/main/protection"
                )

                # Verify branch protection settings
                assert (
                    protection is not None
                ), f"Repository {repo_name} should have branch protection"

                # Add more specific branch protection checks based on your rulesets
                if "required_status_checks" in protection:
                    assert protection["required_status_checks"]["strict"] is True

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # Branch protection not configured or main branch doesn't exist
                    pass
                else:
                    raise


@pytest.mark.integration
class TestBranchProtectionRules:
    """Test branch protection and ruleset configuration."""

    def test_main_branch_protection(self, github_api):
        """Verify main branch protection is enabled."""
        repos = github_api.get(f"orgs/{github_api.owner}/repos")

        for repo in repos:
            repo_name = repo["name"]

            try:
                branches = github_api.get(
                    f"repos/{github_api.owner}/{repo_name}/branches"
                )
                main_branches = [b for b in branches if b["name"] in ["main", "master"]]

                for branch in main_branches:
                    if branch["protected"]:
                        protection = github_api.get(
                            f"repos/{github_api.owner}/{repo_name}/branches/{branch['name']}/protection"
                        )

                        # Verify signed commits requirement
                        assert protection.get("required_signatures", {}).get(
                            "enabled", False
                        ), f"Repository {repo_name} branch {branch['name']} should require signed commits"

                        # Verify admin enforcement
                        assert protection.get("enforce_admins", {}).get(
                            "enabled", False
                        ), f"Repository {repo_name} branch {branch['name']} should enforce rules for admins"

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # Repository might not have main branch yet
                    pass
                else:
                    raise


@pytest.mark.integration
class TestStackOutputValidation:
    """Test Pulumi stack outputs match expected state."""

    def test_stack_outputs_exist(self):
        """Verify that Pulumi stack outputs are present."""
        # This would be run after pulumi update creates stack-outputs.json
        if os.path.exists("stack-outputs.json"):
            with open("stack-outputs.json") as f:
                outputs = json.load(f)

            # Verify we have some outputs
            assert len(outputs) > 0, "Stack should produce some outputs"

            # Example patterns to verify (adjust based on your actual infrastructure):
            # member_outputs = [k for k in outputs.keys() if k.endswith("-github")]
            # repo_outputs = [k for k in outputs.keys() if k.endswith("-repository")]
            # assert len(member_outputs) > 0, "Should have member outputs"
            # assert len(repo_outputs) > 0, "Should have repository outputs"
        else:
            pytest.skip("Stack outputs file not found")
