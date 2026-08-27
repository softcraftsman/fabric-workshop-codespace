#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${repo_root}/.devcontainer/scripts/configure-shell.sh"
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
