#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
venv="${repo_root}/.venv"

for command in git python node npm copilot; do
  command -v "${command}" >/dev/null || {
    echo "Missing required command: ${command}" >&2
    exit 1
  }
done

if [[ ! -x "${venv}/bin/fab" ]]; then
  echo "Fabric CLI is missing. Rebuild the Codespace." >&2
  exit 1
fi

"${venv}/bin/fab" --version
copilot --version

if [[ ! -f "${repo_root}/.workspace/team-context.md" ]]; then
  echo "Workspace context is missing." >&2
  exit 1
fi

echo "Cockpit tooling is available. Fabric sign-in remains user-specific."
