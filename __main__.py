import pulumi
import yaml
import os
import pulumi_github as github
import dotenv
import modules.github.repos as repos
import modules.github.rulesets as rulesets

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

    #Ensure platform team membership
    for platform_members in data.get("github_organization_members", []):
        name = platform_members.get("name")
        username = platform_members.get("github-username")
        role = platform_members.get("github-role", "member")
        email = platform_members.get("email")
        
        # Create a GitHub team member
        team_member = github.Membership(f"github_membership_for_{name}",
            username = f"{username}",
            role = f"{role}"
        )

        # Export the username of the team member
        pulumi.export(f'{username}-github', team_member.username)
    
    for repositories in data.get("github_repositories", []):
        repo_name = repositories.get("name")
        repo_description = repositories.get("description", "")
        
        # Create a GitHub repository
        repository = repos.createRepository(repo_name, repo_description)
        # Set branch protection rules
        ruleset = repository.name.apply(lambda name: 
            rulesets.applyRepositoryRulesets(name, "main")
        )
        

