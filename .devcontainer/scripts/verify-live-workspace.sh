#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
name_file="${repo_root}/.workspace/team-workspace-name"
fab="${repo_root}/.venv/bin/fab"

if [[ ! -s "${name_file}" ]]; then
  echo "Run the Cockpit: Configure team workspace task first." >&2
  exit 1
fi

if [[ ! -x "${fab}" ]]; then
  echo "Fabric CLI is unavailable. Rebuild the Codespace." >&2
  exit 1
fi

workspace_name="$(<"${name_file}")"
error_file="$(mktemp)"
trap 'rm -f "${error_file}"' EXIT

if ! workspace_json="$("${fab}" get "/${workspace_name}.Workspace" --output_format json 2>"${error_file}")"; then
  cat "${error_file}" >&2
  printf '%s\n' "${workspace_json}" >&2
  echo "Fabric CLI could not resolve the exact configured workspace. Check sign-in, tenant, and workspace configuration." >&2
  exit 1
fi
if [[ -s "${error_file}" ]]; then
  cat "${error_file}" >&2
fi

if ! printf '%s' "${workspace_json}" | python \
  "${repo_root}/.devcontainer/scripts/verify_workspace_response.py" \
  "${workspace_name}"; then
  exit 1
fi

echo "Fabric RBAC and Fabric Explorer must still confirm write access."
