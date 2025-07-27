# Integration Test Configuration

This file documents the environment variables needed for the integration tests.

## Required Environment Variables

For the post-deployment integration tests to work, you need to set these environment variables:

### GitHub API Access
```bash
# Your GitHub personal access token with appropriate permissions
export GITHUB_TOKEN="ghp_your_token_here"

# The GitHub organization/owner name to test against
export GITHUB_OWNER="your-org-name"
```

### Setting up Environment Variables

#### For CircleCI
Add these as environment variables in your CircleCI project settings:
1. Go to your CircleCI project
2. Click "Project Settings"
3. Click "Environment Variables"
4. Add:
   - `GITHUB_TOKEN`: Your GitHub PAT
   - `GITHUB_OWNER`: Your organization name

#### For Local Testing

**Option 1: Use Bitwarden (Recommended)**
The post-deployment test script will automatically load secrets from Bitwarden if they're not already set in the environment. This matches the pattern used in `local-deploy.sh`.

Requirements:
- Bitwarden CLI installed: `npm install -g @bitwarden/cli`
- jq installed: `brew install jq`
- `.env` file with Bitwarden credentials:
  ```bash
  BW_CLIENTID=your_bitwarden_client_id
  BW_CLIENTSECRET=your_bitwarden_client_secret
  BW_PASSWORD=your_bitwarden_password
  ```
- A Bitwarden item named "GitHub Secrets" with fields:
  - `pulumi-github-token`: Your GitHub PAT
  - `pulumi-github-owner`: Your organization name

**Option 2: Direct Environment Variables**
Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):
```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_OWNER="your-org-name"
```

Or create a `.env` file in the project root (make sure it's in `.gitignore`):
```bash
GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=your-org-name
```

## GitHub Token Permissions

Your GitHub token needs these permissions for the integration tests:
- **repo**: Full control of private repositories
- **admin:org**: Full control of orgs and teams
- **read:user**: Read access to user profile data

## Running Integration Tests

```bash
# Run only integration tests
uv run pytest test/integration/ -m integration

# Run integration tests with verbose output
uv run pytest test/integration/ -m integration -v

# Skip integration tests (useful for local development)
uv run pytest -m "not integration"
```

## Test Categories

The integration tests are organized into these categories:

1. **Organization Members**: Verify member management and roles
2. **Repositories**: Check repository configuration and settings
3. **Branch Protection**: Validate branch protection rules and rulesets
4. **Stack Outputs**: Verify Pulumi stack outputs match expected state

Each test class is marked with `@pytest.mark.integration` so you can run them selectively.
