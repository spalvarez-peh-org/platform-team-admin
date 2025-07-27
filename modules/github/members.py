import pulumi_github as github
import pulumi

def addPlatformTeamMember(memberInfo):
  name = memberInfo.get("name")
  username = memberInfo.get("github-username")
  role = memberInfo.get("github-role", "member")
        
  # Create a GitHub team member
  team_member = github.Membership(f"github_membership_for_{name}",
    username = f"{username}",
    role = f"{role}"
  )

  # Export the username of the team member
  pulumi.export(f'{username}-github', team_member.username)