#!/usr/bin/env bash
set -euo pipefail

if ! command -v code >/dev/null; then
  echo "VS Code CLI is unavailable. Run this task after the editor connects to the workshop devcontainer." >&2
  exit 1
fi

required_extensions=(
  "github.copilot"
  "github.copilot-chat"
  "fabric.vscode-fabric"
  "fabric.vscode-fabric-mcp-server"
  "analysis-services.tmdl"
  "analysis-services.powerbi-modeling-mcp"
)

installed_extensions="$(code --list-extensions | tr '[:upper:]' '[:lower:]')"
missing=()

for extension in "${required_extensions[@]}"; do
  if ! grep -Fqx "${extension}" <<<"${installed_extensions}"; then
    missing+=("${extension}")
  fi
done

if (( ${#missing[@]} > 0 )); then
  printf 'Missing required extension: %s\n' "${missing[@]}" >&2
  echo "Rebuild the workshop devcontainer or contact the organizer." >&2
  exit 1
fi

echo "GitHub Copilot, Fabric, Fabric MCP, TMDL, and Power BI Modeling MCP extensions are installed."
echo "Open Copilot Chat and send a test prompt to confirm entitlement and policy access."
