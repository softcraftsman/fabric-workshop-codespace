#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
venv="${repo_root}/.venv"

for command in git gh python node npm copilot fabmcp; do
  command -v "${command}" >/dev/null || {
    echo "Workshop setup is incomplete: ${command} is missing." >&2
    echo "Rebuild the workshop devcontainer." >&2
    exit 1
  }
done

if [[ ! -x "${venv}/bin/fab" ]]; then
  echo "Workshop setup is incomplete: Fabric CLI is missing." >&2
  echo "Rebuild the workshop devcontainer." >&2
  exit 1
fi

"${venv}/bin/fab" --version
copilot --version

if [[ ! -f "${repo_root}/.workspace/workshop-context.md" ]]; then
  echo "Workshop setup is incomplete: workspace context is missing." >&2
  echo "Rebuild the workshop devcontainer." >&2
  exit 1
fi

echo "Workshop tooling is ready. Run Fabric: Sign in to authenticate."
