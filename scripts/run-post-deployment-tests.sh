#!/bin/bash

# Post-deployment test runner
# This script runs integration tests to validate the deployed infrastructure

set -euo pipefail

# Parse command line arguments
DRY_RUN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--help]"
      echo ""
      echo "Options:"
      echo "  --dry-run    Show what would be done without actually running tests"
      echo "  --help       Show this help message"
      echo ""
      echo "Environment Variable Sources:"
      echo "  CI: Uses GITHUB_TOKEN and GITHUB_OWNER from CircleCI environment"
      echo "  Local: Loads secrets from Bitwarden using .env file credentials"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Running post-deployment validation tests...${NC}"

if [[ "$DRY_RUN" == true ]]; then
    echo -e "${BLUE}🧪 DRY RUN MODE - showing what would be done${NC}"
fi

# Function to load secrets from Bitwarden (for local runs)
load_secrets_from_bitwarden() {
    echo -e "${BLUE}🔐 Loading secrets from Bitwarden...${NC}"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${BLUE}   [DRY RUN] Would check for Bitwarden CLI and jq${NC}"
        echo -e "${BLUE}   [DRY RUN] Would load .env file for Bitwarden credentials${NC}"
        echo -e "${BLUE}   [DRY RUN] Would login to Bitwarden and retrieve GitHub Secrets${NC}"
        echo -e "${BLUE}   [DRY RUN] Would export GITHUB_TOKEN and GITHUB_OWNER${NC}"
        export GITHUB_TOKEN="dry-run-token"
        export GITHUB_OWNER="dry-run-owner"
        return 0
    fi
    
    # Check if required Bitwarden tools and credentials are available
    if ! command -v bw &> /dev/null; then
        echo -e "${RED}❌ ERROR: Bitwarden CLI (bw) is not installed${NC}"
        echo -e "${YELLOW}   Install with: npm install -g @bitwarden/cli${NC}"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ ERROR: jq is not installed${NC}"
        echo -e "${YELLOW}   Install with: brew install jq${NC}"
        exit 1
    fi
    
    # Load .env file if it exists (for Bitwarden credentials)
    ENV_FILE=".env"
    if [[ -f "$ENV_FILE" ]]; then
        echo -e "${BLUE}📄 Loading Bitwarden credentials from $ENV_FILE${NC}"
        set -o allexport
        source "$ENV_FILE"
        set +o allexport
    fi
    
    # Check Bitwarden credentials
    if [[ -z "${BW_CLIENTID:-}" ]] || [[ -z "${BW_CLIENTSECRET:-}" ]] || [[ -z "${BW_PASSWORD:-}" ]]; then
        echo -e "${RED}❌ ERROR: Bitwarden credentials not found${NC}"
        echo -e "${YELLOW}   Required: BW_CLIENTID, BW_CLIENTSECRET, BW_PASSWORD${NC}"
        echo -e "${YELLOW}   Add these to your .env file or export them directly${NC}"
        exit 1
    fi
    
    # Clean up any existing Bitwarden session
    echo -e "${BLUE}🧹 Cleaning up old Bitwarden CLI session${NC}"
    bw lock &>/dev/null || echo "Vault already locked"
    bw logout &>/dev/null || echo "No active session"
    rm -rf ~/Library/Application\ Support/Bitwarden\ CLI/ &>/dev/null || true
    export BW_SESSION=""
    
    # Login to Bitwarden
    echo -e "${BLUE}🔑 Logging into Bitwarden...${NC}"
    if ! bw login --apikey &>/dev/null; then
        echo -e "${RED}❌ ERROR: Failed to login to Bitwarden${NC}"
        exit 1
    fi
    
    # Unlock vault
    echo -e "${BLUE}🔓 Unlocking vault...${NC}"
    BW_SESSION=$(bw unlock --passwordenv BW_PASSWORD --raw)
    if [[ -z "$BW_SESSION" ]]; then
        echo -e "${RED}❌ ERROR: Failed to unlock Bitwarden vault${NC}"
        exit 1
    fi
    export BW_SESSION
    
    # Retrieve secrets from Bitwarden
    ITEM_NAME="GitHub Secrets"
    echo -e "${BLUE}📥 Retrieving secrets from Bitwarden item: $ITEM_NAME${NC}"
    
    if ! ITEM_JSON=$(bw get item "$ITEM_NAME" --session "$BW_SESSION" 2>/dev/null); then
        echo -e "${RED}❌ ERROR: Failed to retrieve '$ITEM_NAME' from Bitwarden${NC}"
        echo -e "${YELLOW}   Make sure the item exists and contains the required fields${NC}"
        exit 1
    fi
    
    # Extract environment variables
    export GITHUB_TOKEN=$(echo "$ITEM_JSON" | jq -r '.fields[] | select(.name=="pulumi-github-token") | .value')
    export GITHUB_OWNER=$(echo "$ITEM_JSON" | jq -r '.fields[] | select(.name=="pulumi-github-owner") | .value')
    
    if [[ "$GITHUB_TOKEN" == "null" ]] || [[ -z "$GITHUB_TOKEN" ]]; then
        echo -e "${RED}❌ ERROR: pulumi-github-token not found in Bitwarden item${NC}"
        exit 1
    fi
    
    if [[ "$GITHUB_OWNER" == "null" ]] || [[ -z "$GITHUB_OWNER" ]]; then
        echo -e "${RED}❌ ERROR: pulumi-github-owner not found in Bitwarden item${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ GitHub secrets loaded from Bitwarden${NC}"
}

# Check if environment variables are already set (CI environment)
if [[ -n "${GITHUB_TOKEN:-}" ]] && [[ -n "${GITHUB_OWNER:-}" ]]; then
    echo -e "${GREEN}✓ Environment variables already configured (CI environment)${NC}"
elif [[ -n "${CI:-}" ]] || [[ -n "${CIRCLECI:-}" ]]; then
    # In CI but variables not set - this is an error
    echo -e "${RED}❌ ERROR: Running in CI but GITHUB_TOKEN/GITHUB_OWNER not set${NC}"
    exit 1
else
    # Local environment - load from Bitwarden
    load_secrets_from_bitwarden
fi

# Check if stack outputs exist
if [[ -f "stack-outputs.json" ]]; then
    echo -e "${GREEN}✓ Stack outputs file found${NC}"
else
    echo -e "${YELLOW}⚠️  Stack outputs file not found (stack-outputs.json)${NC}"
    echo -e "${YELLOW}   Stack output validation tests will be skipped${NC}"
fi

if [[ "$DRY_RUN" == true ]]; then
    echo -e "${BLUE}🧪 DRY RUN COMPLETE - would run these steps:${NC}"
    echo -e "${BLUE}   1. Install test dependencies with 'uv sync --group test'${NC}"
    echo -e "${BLUE}   2. Run integration tests with pytest${NC}"
    echo -e "${BLUE}   3. Validate GitHub organization state via API${NC}"
    echo -e "${BLUE}   4. Check Pulumi stack outputs if available${NC}"
    echo -e "${GREEN}✅ Dry run completed successfully!${NC}"
    exit 0
fi

# Ensure test dependencies are installed
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
uv sync --group test

# Run integration tests
echo -e "${YELLOW}🧪 Running integration tests...${NC}"

# Use pytest with specific configuration for CI/CD
uv run pytest test/integration/ \
    -m integration \
    --verbose \
    --tb=short \
    --color=yes \
    --durations=10 \
    --strict-markers

exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}✅ All post-deployment tests passed!${NC}"
    echo -e "${GREEN}🎉 Infrastructure validation successful${NC}"
else
    echo -e "${RED}❌ Post-deployment tests failed${NC}"
    echo -e "${RED}💥 Infrastructure validation failed${NC}"
    exit $exit_code
fi
