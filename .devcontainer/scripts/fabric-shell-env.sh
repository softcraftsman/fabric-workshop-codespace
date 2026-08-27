#!/usr/bin/env bash

_fabric_workshop_load_tokens() {
  local config_dir="${XDG_CONFIG_HOME:-${HOME}/.config}/fabric-workshop"
  local tenant_file="${config_dir}/tenant-id"
  local tenant_id
  local fabric_token
  local onelake_token
  local azure_token

  [[ -r "${tenant_file}" ]] || return 0

  if ! command -v az >/dev/null; then
    echo "Fabric authentication is unavailable because Azure CLI is missing." >&2
    return 0
  fi

  tenant_id="$(<"${tenant_file}")"
  if ! fabric_token="$(az account get-access-token \
    --tenant "${tenant_id}" \
    --resource https://analysis.windows.net/powerbi/api \
    --query accessToken \
    --output tsv 2>/dev/null)" ||
    ! onelake_token="$(az account get-access-token \
      --tenant "${tenant_id}" \
      --resource https://storage.azure.com \
      --query accessToken \
      --output tsv 2>/dev/null)" ||
    ! azure_token="$(az account get-access-token \
      --tenant "${tenant_id}" \
      --resource https://management.azure.com \
      --query accessToken \
      --output tsv 2>/dev/null)"; then
    unset FAB_TENANT_ID FAB_TOKEN FAB_TOKEN_ONELAKE FAB_TOKEN_AZURE
    echo "Fabric authentication expired. Run Fabric: Sign in again." >&2
    return 0
  fi

  export FAB_TENANT_ID="${tenant_id}"
  export FAB_TOKEN="${fabric_token}"
  export FAB_TOKEN_ONELAKE="${onelake_token}"
  export FAB_TOKEN_AZURE="${azure_token}"
}

_fabric_workshop_load_tokens
unset -f _fabric_workshop_load_tokens
