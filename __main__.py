import yaml
import os
import pulumi_github as github
import dotenv
import modules.github.repos as repos
import modules.github.rulesets as rulesets
import modules.github.members as members

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
    for platform_member in data.get("github_organization_members", []):
        members.addPlatformTeamMember(platform_member)
    
    #Add Repositories and configuration
    for repositories in data.get("github_repositories", []):
        repo_name = repositories.get("name")
        repo_description = repositories.get("description", "")
        
        # Create a GitHub repository
        repository = repos.createRepository(repo_name, repo_description)
        # Set branch protection rules
        ruleset = repository.name.apply(lambda name: 
            rulesets.applyRepositoryRulesets(name, "main")
        )
        

