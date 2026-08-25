#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fab="${repo_root}/.venv/bin/fab"
tenant_id="${1:-${FAB_TENANT_ID:-}}"

tenant_id="${tenant_id#"${tenant_id%%[![:space:]]*}"}"
tenant_id="${tenant_id%"${tenant_id##*[![:space:]]}"}"

if [[ -z "${tenant_id}" ]]; then
  echo "A Microsoft Entra tenant ID is required." >&2
  echo "Usage: $0 <tenant-id>" >&2
  exit 1
fi

if [[ ! "${tenant_id}" =~ ^[[:xdigit:]]{8}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{12}$ ]]; then
  echo "Tenant ID must be a GUID." >&2
  exit 1
fi

command -v az >/dev/null || {
  echo "Azure CLI is missing. Rebuild the Codespace to install it." >&2
  exit 1
}

if [[ ! -x "${fab}" ]]; then
  echo "Fabric CLI is missing. Rebuild the Codespace." >&2
  exit 1
fi

az login \
  --use-device-code \
  --tenant "${tenant_id}" \
  --allow-no-subscriptions \
  --output none

# Clear a persisted service-principal or managed-identity mode, which takes
# precedence over externally supplied user tokens in Fabric CLI.
"${fab}" auth logout >/dev/null 2>&1 || true

export FAB_TENANT_ID="${tenant_id}"
export FAB_TOKEN
FAB_TOKEN="$(az account get-access-token \
  --tenant "${tenant_id}" \
  --resource https://api.fabric.microsoft.com \
  --query accessToken \
  --output tsv)"
export FAB_TOKEN_ONELAKE
FAB_TOKEN_ONELAKE="$(az account get-access-token \
  --tenant "${tenant_id}" \
  --resource https://storage.azure.com \
  --query accessToken \
  --output tsv)"
export FAB_TOKEN_AZURE
FAB_TOKEN_AZURE="$(az account get-access-token \
  --tenant "${tenant_id}" \
  --resource https://management.azure.com \
  --query accessToken \
  --output tsv)"

"${fab}" auth status

if [[ -s "${repo_root}/.workspace/team-workspace-name" ]]; then
  bash "${repo_root}/.devcontainer/scripts/verify-live-workspace.sh"
else
  echo "Workspace verification skipped because no writable workspace is configured." >&2
fi

cat <<'MESSAGE'

Opening an authenticated Fabric CLI shell.
Run all Fabric CLI commands in this shell, then run "exit" when finished.
Tokens are temporary and are not written to the repository or inherited by
other VS Code task terminals.
MESSAGE

exec "${SHELL:-/bin/bash}" -i