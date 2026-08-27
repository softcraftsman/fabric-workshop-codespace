#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
venv="${repo_root}/.venv"

python -m venv "${venv}"
# shellcheck disable=SC1091
source "${venv}/bin/activate"

python -m pip install --upgrade pip wheel
python -m pip install --requirement "${repo_root}/.devcontainer/requirements.txt"
npm install --global "@github/copilot@latest"
npm install --global "@microsoft/fabric-mcp@latest"

"${venv}/bin/fab" config set encryption_fallback_enabled true
