#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
venv="${repo_root}/.venv"

python -m venv "${venv}"
# shellcheck disable=SC1091
source "${venv}/bin/activate"

python -m pip install --upgrade pip wheel
python -m pip install --requirement "${repo_root}/.devcontainer/requirements.txt"
npm install --global "@github/copilot@${COPILOT_CLI_VERSION:?}"

bash "${repo_root}/.devcontainer/scripts/configure-workspace.sh"
bash "${repo_root}/.devcontainer/scripts/verify-environment.sh"

cat <<'MESSAGE'

Fabric Workshop Cockpit is ready.

1. Run "Codespace: Verify required extensions".
2. Open Copilot Chat and send a test prompt.
3. Run "copilot" and use /login if authentication is required.
4. Confirm the organizer configured .cockpit/workshop.json.
5. Run "Codespace: Configure team workspace".
6. Run "Fabric: Sign in" and select the correct tenant.
7. Run "Fabric CLI: Sign in". Use the device-code task in browser Codespaces.
8. Confirm the same workspace in Fabric Explorer and Fabric CLI.
9. Open README.md before modifying a live Fabric item.

MESSAGE
