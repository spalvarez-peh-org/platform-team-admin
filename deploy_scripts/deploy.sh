#!/bin/bash
set -euo pipefail

VERBOSE=false
# Default action
ACTION="up"
#Default stack
PULUMI_STACK="dev"

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
    --help|-h)
      echo "Usage: $0 [--action up|destroy|preview] [--stack dev|prod] [--verbose]"
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

if bw status | grep -q '"status": "unlocked"'; then
  echo "🔒 Bitwarden already unlocked. Logging out to start fresh..."
  bw logout
fi

echo "Logging into Bitwarden..."
bw login --apikey -quiet

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

if [[ ! -d ".venv" ]]; then
  echo "Creating virtual environment..."
  uv venv .venv
fi

source .venv/bin/activate
uv pip install -r requirements.txt
pulumi stack select $PULUMI_STACK

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