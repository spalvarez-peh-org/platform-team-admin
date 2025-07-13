#!/bin/bash
set -euo pipefail

CCI_ORG_ID="$1"
CONTEXT_NAME=PLATFORM_ADMIN

# Load .env before accessing any env vars
ENV_FILE=".env"
if [[ ! -f "${ENV_FILE}" ]]; then
  echo ".env file not found at $ENV_FILE"
  exit 1
fi

# Load secrets from env file
set -o allexport
source "${ENV_FILE}"
set +o allexport

circleci context create --org-id "${CCI_ORG_ID}" "${CONTEXT_NAME}"

while IFS='=' read -r key val; do
  [[ -z "$key" ]] && continue
  echo "Adding $key"
  circleci context store-secret --org-id ${CCI_ORG_ID} ${CONTEXT_NAME} $key <<< "$val"
done < <(grep -v '^#' "$ENV_FILE")