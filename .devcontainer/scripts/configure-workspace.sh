#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if (( $# > 0 )); then
  workspace_name="$1"
  if [[ -z "${workspace_name//[[:space:]]/}" ]]; then
    echo "Workspace name cannot be empty." >&2
    exit 1
  fi
else
  workspace_name="${TEAM_WORKSPACE_NAME:-}"
fi

exec python "${repo_root}/.devcontainer/scripts/configure_workspace.py" \
  "${workspace_name}"
