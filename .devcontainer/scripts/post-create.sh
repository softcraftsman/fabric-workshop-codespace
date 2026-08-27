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

"${venv}/bin/fab" config set encryption_fallback_enabled true

bash "${repo_root}/.devcontainer/scripts/configure-workspace.sh"
bash "${repo_root}/.devcontainer/scripts/verify-environment.sh"

cat <<'MESSAGE'

Fabric Workshop Codespace is ready.

Participant setup:
1. Sign in to Fabric Explorer with your workshop identity.
2. Run "Fabric: Sign in".
3. Enter your assigned workspace and commercial-cloud work email when prompted.
4. Complete the device-code prompt and keep the authenticated shell open.
5. Confirm Fabric Explorer and Fabric CLI show the same workspace.

MESSAGE
