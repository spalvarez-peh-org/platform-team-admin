import dotenv
import pulumi_bitwarden as bitwarden
import pulumi_github as github
import yaml

dotenv.load_dotenv()
github_secrets = bitwarden.get_item_login_output(search="GitHub Secrets")

# Explicitly configure the provider with those values
provider = github.Provider(
    "custom-github-provider",
    owner=github_secrets.username,
    token=github_secrets.password,
)

# Load the values file
with open("config/platform_team_values.yaml") as f:
    data = yaml.safe_load(f)

    # Ensure platform team membership
    for team_member in data.get("github_organization_members", []):
        name = team_member.get("name")
        username = team_member.get("github-username")
        role = team_member.get("github-role", "member")

        # Create a GitHub team member
        team_member = github.Membership(
            f"github_membership_for_{name}", username=f"{username}", role=f"{role}"
        )

    # Add Repositories and configuration
    for repositories in data.get("github_repositories", []):
        repo_name = repositories.get("name")
        repo_description = repositories.get("description", "")

        # Create a GitHub repository
        repository = github.Repository(
            f"{repo_name}",
            name=repo_name,
            description=repo_description,
            visibility="public",
        )

        # Create a branch protection rule that enforces signed commits
        branch_protection = github.BranchProtection(
            f"{repo_name}-main-branch-protection",
            repository_id=repo_name,
            pattern="main",
            enforce_admins=True,
            require_signed_commits=True,
        )
