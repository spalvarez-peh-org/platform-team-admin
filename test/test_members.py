"""
Unit tests for the GitHub members module.

Tests the addPlatformTeamMember function which creates GitHub organization memberships
using Pulumi and pulumi-github provider.
"""

from unittest.mock import call

import pytest

from modules.github.members import addPlatformTeamMember


class TestAddPlatformTeamMember:
    """Test cases for the addPlatformTeamMember function."""

    def test_add_member_with_complete_info(
        self, patch_github_members, valid_member_complete, assertions
    ):
        """Test adding a member with all required information."""
        mock_pulumi, mock_github = patch_github_members

        addPlatformTeamMember(valid_member_complete)

        # Use centralized assertion helper
        assertions.assert_membership_called_with(
            mock_github,
            f"github_membership_for_{valid_member_complete['name']}",
            valid_member_complete["github-username"],
            valid_member_complete["github-role"],
        )

        # Verify pulumi export was called
        assertions.assert_pulumi_export_called_with(
            mock_pulumi,
            f"{valid_member_complete['github-username']}-github",
            mock_github.Membership.return_value.username,
        )

    def test_add_member_with_default_role(
        self, patch_github_members, valid_member_minimal, assertions
    ):
        """Test adding a member without specifying role (should default to 'member')."""
        mock_pulumi, mock_github = patch_github_members

        addPlatformTeamMember(valid_member_minimal)

        # Verify GitHub Membership was created with default role
        assertions.assert_membership_called_with(
            mock_github,
            f"github_membership_for_{valid_member_minimal['name']}",
            valid_member_minimal["github-username"],
            "member",  # Default role
        )

        # Verify pulumi export was called
        assertions.assert_pulumi_export_called_with(
            mock_pulumi,
            f"{valid_member_minimal['github-username']}-github",
            mock_github.Membership.return_value.username,
        )

    def test_add_member_with_minimal_info(self, patch_github_members, assertions):
        """Test adding a member with only name and username."""
        mock_pulumi, mock_github = patch_github_members

        member_info = {"name": "Bob Wilson", "github-username": "bobwilson"}

        addPlatformTeamMember(member_info)

        # Verify GitHub Membership was created with minimal info
        assertions.assert_membership_called_with(
            mock_github, "github_membership_for_Bob Wilson", "bobwilson", "member"
        )

    def test_add_member_with_missing_name(self, patch_github_members, assertions):
        """Test adding a member when name is missing (should handle gracefully)."""
        mock_pulumi, mock_github = patch_github_members

        member_info = {"github-username": "testuser", "github-role": "member"}

        addPlatformTeamMember(member_info)

        # Verify GitHub Membership was created with None name
        assertions.assert_membership_called_with(
            mock_github, "github_membership_for_None", "testuser", "member"
        )

    def test_add_member_with_missing_username(self, patch_github_members, assertions):
        """Test adding a member when username is missing (should handle gracefully)."""
        mock_pulumi, mock_github = patch_github_members

        member_info = {"name": "Test User", "github-role": "admin"}

        addPlatformTeamMember(member_info)

        # Verify GitHub Membership was created with None username
        assertions.assert_membership_called_with(
            mock_github,
            "github_membership_for_Test User",
            "None",  # String representation of None
            "admin",
        )

    def test_add_member_with_empty_dict(
        self, patch_github_members, empty_dict, assertions
    ):
        """Test adding a member with empty member info dictionary."""
        mock_pulumi, mock_github = patch_github_members

        addPlatformTeamMember(empty_dict)

        # Verify GitHub Membership was created with None values
        assertions.assert_membership_called_with(
            mock_github, "github_membership_for_None", "None", "member"  # Default role
        )

    def test_add_member_with_different_roles(
        self, patch_github_members, github_roles, assertions
    ):
        """Test adding members with different valid GitHub roles."""
        mock_pulumi, mock_github = patch_github_members
        role, expected = github_roles

        member_info = {
            "name": f"Test User {role}",
            "github-username": f"testuser_{role}",
            "github-role": role,
        }

        addPlatformTeamMember(member_info)

        # Verify role was set correctly
        assertions.assert_membership_called_with(
            mock_github,
            f"github_membership_for_Test User {role}",
            f"testuser_{role}",
            expected,
        )

    def test_export_name_format(self, patch_github_members, assertions):
        """Test that the export name is formatted correctly."""
        mock_pulumi, mock_github = patch_github_members

        member_info = {
            "name": "Export Test User",
            "github-username": "export-test-user",
            "github-role": "member",
        }

        addPlatformTeamMember(member_info)

        # Verify export was called with correct format
        expected_export_name = "export-test-user-github"
        assertions.assert_pulumi_export_called_with(
            mock_pulumi,
            expected_export_name,
            mock_github.Membership.return_value.username,
        )

    def test_resource_name_with_special_characters(
        self, patch_github_members, assertions
    ):
        """Test resource naming with special characters in name."""
        mock_pulumi, mock_github = patch_github_members

        member_info = {
            "name": "Test User-O'Connor",
            "github-username": "test-user",
            "github-role": "member",
        }

        addPlatformTeamMember(member_info)

        # Verify resource name includes special characters
        expected_resource_name = "github_membership_for_Test User-O'Connor"
        assertions.assert_membership_called_with(
            mock_github, expected_resource_name, "test-user", "member"
        )

    def test_membership_object_created(self, patch_github_members):
        """Test that the membership object is created properly."""
        mock_pulumi, mock_github = patch_github_members

        member_info = {
            "name": "Return Test",
            "github-username": "returntest",
        }

        addPlatformTeamMember(member_info)

        # Verify the membership object was created
        assert mock_github.Membership.called
        assert mock_github.Membership.call_count == 1


@pytest.mark.integration
class TestAddPlatformTeamMemberIntegration:
    """Integration-style tests that verify the interaction between components."""

    def test_full_workflow_integration(self, patch_github_members, assertions):
        """Test the complete workflow from input to output."""
        mock_pulumi, mock_github = patch_github_members

        member_info = {
            "name": "Integration Test User",
            "github-username": "integration-test-user",
            "github-role": "admin",
        }

        # Execute
        addPlatformTeamMember(member_info)

        # Verify the complete workflow
        assertions.assert_membership_called_with(
            mock_github,
            "github_membership_for_Integration Test User",
            "integration-test-user",
            "admin",
        )

        assertions.assert_pulumi_export_called_with(
            mock_pulumi,
            "integration-test-user-github",
            mock_github.Membership.return_value.username,
        )

    def test_multiple_members_workflow(self, patch_github_members):
        """Test adding multiple members in sequence."""
        mock_pulumi, mock_github = patch_github_members

        members = [
            {"name": "User One", "github-username": "user1", "github-role": "admin"},
            {"name": "User Two", "github-username": "user2", "github-role": "member"},
            {"name": "User Three", "github-username": "user3"},  # No role specified
        ]

        # Execute
        for member in members:
            addPlatformTeamMember(member)

        # Verify all members were processed
        assert mock_github.Membership.call_count == 3
        assert mock_pulumi.export.call_count == 3

        # Verify specific calls
        expected_calls = [
            call("github_membership_for_User One", username="user1", role="admin"),
            call("github_membership_for_User Two", username="user2", role="member"),
            call("github_membership_for_User Three", username="user3", role="member"),
        ]
        mock_github.Membership.assert_has_calls(expected_calls)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_none_input(self, patch_github_members):
        """Test behavior when None is passed as member_info."""
        mock_pulumi, mock_github = patch_github_members

        # This should raise an AttributeError since None doesn't have .get()
        with pytest.raises(AttributeError):
            addPlatformTeamMember(None)

    def test_non_dict_input(self, patch_github_members):
        """Test behavior when non-dictionary is passed as member_info."""
        mock_pulumi, mock_github = patch_github_members

        # This should raise an AttributeError since strings don't have .get()
        with pytest.raises(AttributeError):
            addPlatformTeamMember("not a dict")

    def test_with_fixture_data(
        self, patch_github_members, valid_member_complete, assertions
    ):
        """Test using pytest fixture data."""
        mock_pulumi, mock_github = patch_github_members

        addPlatformTeamMember(valid_member_complete)

        # Verify the call was made correctly using centralized assertion
        assertions.assert_membership_called_with(
            mock_github,
            f"github_membership_for_{valid_member_complete['name']}",
            valid_member_complete["github-username"],
            valid_member_complete["github-role"],
        )
