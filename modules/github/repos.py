import pulumi
import pulumi_github as github


def createRepository(repo_name: str, repo_description: str | None) -> github.Repository:
    # Create a GitHub repository
    repository = github.Repository(
        f"{repo_name}",
        name=repo_name,
        description=repo_description,
        visibility="public",
        opts=pulumi.ResourceOptions(protect=True),
    )
    pulumi.export(f"{repo_name}-repository", repository.name)

    return repository
