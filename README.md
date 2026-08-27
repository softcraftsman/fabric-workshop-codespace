# Fabric Workshop Codespace

A reusable GitHub Codespaces control surface for Microsoft Fabric workshops.
Participants receive consistent Fabric, Copilot, semantic-modeling, notebook,
Python, and SQL tooling while Fabric remains the runtime, collaboration, and
security boundary.

## Participant start

1. Open Fabric Explorer from the Fabric icon in the Activity Bar. Sign in and
   select the organizer-designated Microsoft Entra tenant.
2. Run **Tasks: Run Task > Fabric: Sign in** and enter your commercial-cloud
   work email or tenant domain.
3. Complete the device-code prompt in your browser. The task resolves the
   tenant and opens an authenticated shell.
4. Run Fabric CLI commands in that shell or any new Bash terminal. Reopen
   terminals that were already open when you signed in.
5. Before every modification, confirm the live target workspace, item name,
   item type, and proposed change.

## Installed tools

| Area | Tools |
|---|---|
| Command line | Python 3.12, Azure CLI, GitHub CLI, Node.js 22, Microsoft Fabric CLI, GitHub Copilot CLI |
| Fabric | Microsoft Fabric extension, Fabric MCP Server |
| Modeling | TMDL, Power BI Modeling MCP |
| Development | GitHub Copilot, Python, Pylance, Jupyter, SQL Server |

Fabric CLI is pinned in `.devcontainer/requirements.txt`; Copilot CLI and the
Fabric MCP Server are pinned in `.devcontainer/devcontainer.json`.

## Optional workshop customization

This repository works with its default
[`.codespace/workshop.json`](.codespace/workshop.json). Organizers may
optionally customize it for a specific workshop:

1. Set the workshop name, protected workspaces, data-handling rules, and
   workshop instructions.
2. Review [organizer setup](guidance/organizer-setup.md).
3. Launch a clean Codespace and complete the participant-equivalent acceptance
   test before distributing the repository.

The [Multi-AMC example](.codespace/multi-amc-workshop.json) shows how a workshop
profile can add domain-specific protections without changing the reusable
Codespace.

## Safety model

Copilot instructions are guardrails, not an authorization boundary. Fabric
RBAC must grant write access only where each participant is expected to work.

Before saving a Fabric item:

1. Inspect and explain the existing item.
2. Confirm the workspace, item name, item type, inputs, outputs, and bindings.
3. Propose the smallest necessary change.
4. Review the complete definition.
5. Save and validate the result in Fabric.

See [safety and recovery](guidance/safety-and-recovery.md) for operational
controls and recovery expectations.

## Repository structure

| Path | Purpose |
|---|---|
| `.codespace/` | Workshop configuration, schema, and example profile |
| `.devcontainer/` | Codespaces image, installation, authentication, and verification |
| `.github/copilot-instructions.md` | Reusable mutation guardrails |
| `.github/mcp.json` | Repository-level Fabric MCP registration for Copilot CLI |
| `.vscode/` | Participant tasks and editor defaults |
| `guidance/` | Organizer and participant safety guidance |
| `tests/` | Configuration and workflow tests |

## Updating dependencies

Review pinned Fabric CLI and Copilot CLI versions monthly and before every
event. Update one tool at a time, open a pull request, allow both validation
workflows to pass, then complete the clean-Codespace acceptance test before
merging. Rebuild Codespaces prebuilds after any devcontainer change.
