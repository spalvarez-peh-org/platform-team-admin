#!/bin/bash
set -euo pipefail

VERBOSE=false
# Default action
ACTION="up"
#Default stack
PULUMI_STACK="dev"
# Default: run quality checks
SKIP_QUALITY_CHECKS=false

#parse optional flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --action)
      ACTION="$2"
      shift 2
      ;;
    --stack)
      PULUMI_STACK="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --skip-quality-checks)
      SKIP_QUALITY_CHECKS=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--action up|destroy|preview] [--stack dev|prod] [--verbose] [--skip-quality-checks]"
      echo ""
      echo "Options:"
      echo "  --action              Pulumi action: up, destroy, or preview (default: up)"
      echo "  --stack               Pulumi stack: dev or prod (default: dev)"
      echo "  --verbose             Enable verbose output"
      echo "  --skip-quality-checks Skip static analysis, tests, and quality checks"
      echo ""
      echo "This script mimics the CircleCI pipeline locally with environment variables from .env"
      echo ""
      echo "After deployment, run post-deployment tests with:"
      echo "  ./scripts/run-post-deployment-tests.sh"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ "$VERBOSE" == true ]]; then
  set -x
fi

# Ensure required commands are available
for cmd in jq bw pulumi uv; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is not installed or not in PATH."
    exit 1
  fi
done

echo "🚀 Starting local deployment pipeline (mimicking CircleCI)..."

# Setup Python environment (matching CircleCI pattern)
echo "📦 Setting up Python environment..."
if [[ -d ".venv" ]]; then
  echo "Clearing existing virtual environment..."
  rm -rf .venv
fi

echo "Creating fresh virtual environment..."
uv venv --clear
uv add -r requirements.txt
uv sync --group lint --group test

# Load .env before accessing any env vars
ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo ".env file not found at $ENV_FILE"
  exit 1
fi

# Load secrets from env file
set -o allexport
source "$ENV_FILE"
set +o allexport

# Ensure Bitwarden credentials are set
: "${BW_CLIENTID:?BW_CLIENTID must be set}"
: "${BW_CLIENTSECRET:?BW_CLIENTSECRET must be set}"
: "${BW_PASSWORD:?BW_PASSWORD must be set}"

echo "Cleaning up old Bitwarden CLI session"
bw lock || echo "Vault already locked"
bw logout || echo "No active session"
rm -rf ~/Library/Application\ Support/Bitwarden\ CLI/
export BW_SESSION=""

echo "Logging into Bitwarden..."
bw login --apikey

echo "Unlocking vault..."
BW_SESSION=$(bw unlock --passwordenv BW_PASSWORD --raw)
export BW_SESSION

# Name of the Bitwarden item containing the secrets
ITEM_NAME="GitHub Secrets"

echo "Retrieving secrets from Bitwarden item: $ITEM_NAME"
ITEM_JSON=$(bw get item "$ITEM_NAME" --session "$BW_SESSION")

# Load environment variables
export GITHUB_TOKEN=$(echo "$ITEM_JSON" | jq -r '.fields[] | select(.name=="pulumi-github-token") | .value')
export GITHUB_OWNER=$(echo "$ITEM_JSON" | jq -r '.fields[] | select(.name=="pulumi-github-owner") | .value')

echo "GitHub secrets loaded into environment variables"

# Quality checks (matching CircleCI pipeline)
if [[ "$SKIP_QUALITY_CHECKS" == false ]]; then
  echo ""
  echo "🔍 Running quality checks (matching CircleCI pipeline)..."
  
  echo "1️⃣ Static analysis (ruff)..."
  uv run ruff check .
  
  echo "2️⃣ Type checking (mypy)..."
  uv run mypy __main__.py modules/ --explicit-package-bases --ignore-missing-imports --show-error-codes
  
  echo "3️⃣ Security scanning (bandit)..."
  uv run bandit -r __main__.py modules/ -ll
  
  echo "4️⃣ Format checking (black)..."
  uv run black --check --diff __main__.py modules/ test/
  
  echo "5️⃣ Import sorting (isort)..."
  uv run isort --check-only --diff __main__.py modules/ test/
  
  echo "6️⃣ Unit tests..."
  uv run pytest test/ -v --tb=short
  
  echo "7️⃣ Coverage verification..."
  uv run pytest test/ --cov=modules --cov-report=term --cov-report=html --cov-fail-under=90
  
  echo "✅ All quality checks passed!"
else
  echo "⚠️  Skipping quality checks (--skip-quality-checks flag used)"
fi

echo ""
echo "🏗️ Preparing Pulumi environment..."

echo "🏗️ Preparing Pulumi environment..."

# Pulumi setup (matching CircleCI load-pulumi-environment)
pulumi login
uv venv --clear
uv add -r requirements.txt
uv sync
pulumi stack select $PULUMI_STACK

echo ""
echo "🚀 Running Pulumi deployment..."

# Run Pulumi with specified action
case "$ACTION" in
  up)
    echo "Running: pulumi up -y"
    pulumi up -y
    ;;
  destroy)
    echo "Running: pulumi destroy -y"
    pulumi destroy -y
    ;;
  preview)
    echo "Running: pulumi preview"
    pulumi preview
    ;;
  *)
    echo "Invalid action: $ACTION. Use 'up', 'destroy', or 'preview'."
    exit 1
    ;;
esac

echo ""
echo "🎉 Local deployment pipeline completed successfully!"
echo "📊 Summary:"
echo "   Stack: $PULUMI_STACK"
echo "   Action: $ACTION"
echo "   Quality checks: $([ "$SKIP_QUALITY_CHECKS" == true ] && echo "SKIPPED" || echo "PASSED")"
echo ""
echo "💡 Next step: Run post-deployment validation tests:"
echo "   ./scripts/run-post-deployment-tests.sh"