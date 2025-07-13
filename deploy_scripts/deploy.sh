#!/bin/bash
set -euo pipefail

# 🏷️ Default action
ACTION="up"

# Parse optional --action flag
while [[ $# -gt 0 ]]; do
  case "$1" in
    --action)
      ACTION="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Load .env before accessing any env vars
# ENV_FILE=".env"
# if [[ ! -f "$ENV_FILE" ]]; then
#   echo ".env file not found at $ENV_FILE"
#   exit 1
# fi

# # Load secrets from env file
# set -o allexport
# source "$ENV_FILE"
# set +o allexport

# Ensure Bitwarden credentials are set
: "${BW_CLIENTID:?BW_CLIENTID must be set}"
: "${BW_CLIENTSECRET:?BW_CLIENTSECRET must be set}"
: "${BW_PASSWORD:?BW_PASSWORD must be set}"


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

bw logout --quiet

echo "GitHub secrets loaded into environment variables"

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