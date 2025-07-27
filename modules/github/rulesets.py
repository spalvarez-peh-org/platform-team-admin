import pulumi_github as github


def applyRepositoryRulesets(
    repo_name: str, branch_name: str
) -> github.BranchProtection:
    # Create a branch protection rule that enforces signed commits
    branch_protection = github.BranchProtection(
        f"{repo_name}-{branch_name}-branch-protection",
        repository_id=repo_name,
        pattern=branch_name,
        enforce_admins=True,
        require_signed_commits=True,
    )

    return branch_protection
