#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fab="${repo_root}/.venv/bin/fab"
tenant_lookup="${1:-${FAB_TENANT_DOMAIN:-${FAB_TENANT_ID:-}}}"

tenant_lookup="${tenant_lookup#"${tenant_lookup%%[![:space:]]*}"}"
tenant_lookup="${tenant_lookup%"${tenant_lookup##*[![:space:]]}"}"

if [[ "${CODESPACES:-false}" != "true" && ! -f "/.dockerenv" ]]; then
  echo "Fabric: Sign in must run inside the workshop devcontainer." >&2
  echo "Rebuild and reopen the repository in the devcontainer, then run" >&2
  echo "Fabric: Sign in again." >&2
  exit 1
fi

if [[ -z "${tenant_lookup}" ]]; then
  echo "Your work email or Microsoft Entra tenant domain is required." >&2
  echo "Usage: $0 <work-email-or-domain>" >&2
  exit 1
fi

command -v az >/dev/null || {
  echo "Workshop setup is incomplete: Azure CLI is missing." >&2
  echo "Rebuild the workshop devcontainer, then run Fabric: Sign in again." >&2
  exit 1
}

if [[ ! -x "${fab}" ]]; then
  echo "Workshop setup is incomplete: Fabric CLI is missing." >&2
  echo "Rebuild the workshop devcontainer, then run Fabric: Sign in again." >&2
  exit 1
fi

if [[ ! -s "${repo_root}/.workspace/team-workspace-name" ]]; then
  if [[ ! -t 0 ]]; then
    echo "No writable Fabric workspace is configured." >&2
    echo "Run Codespace: Configure team workspace, then run Fabric: Sign in." >&2
    exit 1
  fi

  read -r -p "Enter your assigned writable Fabric workspace: " workspace_name
  bash "${repo_root}/.devcontainer/scripts/configure-workspace.sh" \
    "${workspace_name}"
fi

tenant_id="$(python "${repo_root}/.devcontainer/scripts/resolve_tenant.py" \
  "${tenant_lookup}")"
echo "Signing in to Microsoft Entra tenant ${tenant_id}."

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
  --resource https://analysis.windows.net/powerbi/api \
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

bash "${repo_root}/.devcontainer/scripts/verify-live-workspace.sh"

cat <<'MESSAGE'

Fabric sign-in and workspace verification succeeded.
Use the authenticated shell opening now for all Fabric CLI commands.
When finished, run "exit". Temporary tokens remain in this shell and are
not written to the repository or shared with other task terminals.
MESSAGE

exec "${SHELL:-/bin/bash}" -i