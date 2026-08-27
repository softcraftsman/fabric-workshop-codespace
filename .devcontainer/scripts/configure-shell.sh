#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
shell_env="${repo_root}/.devcontainer/scripts/fabric-shell-env.sh"
source_line="source \"${shell_env}\""

python "${repo_root}/.devcontainer/scripts/configure_copilot.py" "${repo_root}"

touch "${HOME}/.bashrc"
if ! grep -Fqx "${source_line}" "${HOME}/.bashrc"; then
  printf '\n%s\n' "${source_line}" >>"${HOME}/.bashrc"
fi
