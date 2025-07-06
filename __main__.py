import pulumi
import yaml
import os
import pulumi_github as github
import dotenv

dotenv.load_dotenv()

# Get GitHub credentials from env
token = os.getenv("GITHUB_TOKEN")
owner = os.getenv("GITHUB_OWNER")

# Explicitly configure the provider with those values
provider = github.Provider("custom-github-provider",
    token=token,
    owner=owner,
)

# Load the values file
with open("config/platform_team_values.yaml", "r") as f:
    data = yaml.safe_load(f)

    # Load the BitWarden organization ID from the environment variable
    org_id = os.getenv("BW_ORG_ID")

    #Ensure platform team membership
    # for platform_members in data.get("github_organization_members", []):
    #     name = platform_members.get("name")
    #     username = platform_members.get("github-username")
    #     role = platform_members.get("github-role", "member")
    #     email = platform_members.get("email")
        
    #     # Create a GitHub team member
    #     team_member = github.Membership(f"github_membership_for_{name}",
    #         username = f"{username}",
    #         role = f"{role}"
    #     )

    #     # Export the username of the team member
    #     pulumi.export(f'{username}-github', team_member.username)

    # Create each repository
    for repo in data.get("github_repositories", []):
        name = repo.get("name")
        description = repo.get("description", "")
        
        # Create a GitHub repository
        repository = github.Repository(f"{name}", 
        name=name,
        description=f"{description}"
        )

        # Export the Name of the repository
        pulumi.export(f'{name}-repository', repository.name)