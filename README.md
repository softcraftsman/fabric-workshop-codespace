# Fabric Workshop Cockpit

A reusable GitHub Codespaces control surface for Microsoft Fabric workshops.
Participants receive consistent Fabric, Copilot, semantic-modeling, notebook,
Python, and SQL tooling while Fabric remains the runtime, collaboration, and
security boundary.

## Organizer setup

This repository fails closed until an organizer customizes
[`.cockpit/workshop.json`](.cockpit/workshop.json):

1. Create a repository from this GitHub template.
2. Set the workshop name, workspace-name rule, protected workspaces,
   data-handling rules, and workshop instructions.
3. Set `configured` to `true`.
4. Review [organizer setup](guidance/organizer-setup.md).
5. Launch a clean Codespace and complete the participant-equivalent acceptance
   test before distributing the repository.

The [Multi-AMC example](examples/multi-amc-workshop.json) shows how a workshop
profile can add domain-specific protections without changing the reusable
cockpit.

## Participant start

1. Open Fabric Explorer from the Fabric icon in the Activity Bar. Sign in and
   select the organizer-designated Microsoft Entra tenant.
2. Select your assigned workspace in Fabric Explorer.
3. Run **Tasks: Run Task > Cockpit: Configure team workspace** and enter the
   exact same workspace name.
4. Run **Fabric CLI: Sign in** and then **Fabric CLI: Verify configured
   workspace**.
5. If normal sign-in cannot complete, run **Fabric CLI: Sign in with device
   code**. That task verifies the workspace automatically and opens an
   authenticated shell; run subsequent Fabric CLI commands inside that shell.
6. Confirm Fabric Explorer and Fabric CLI identify the same workspace before
   creating or changing an item.

## Installed tools

| Area | Tools |
|---|---|
| Command line | Python 3.12, Azure CLI, Node.js 22, Microsoft Fabric CLI, GitHub Copilot CLI |
| Fabric | Microsoft Fabric extension, Fabric MCP Server |
| Modeling | TMDL, Power BI Modeling MCP |
| Development | GitHub Copilot, Python, Pylance, Jupyter, SQL Server |

Fabric CLI is pinned in `.devcontainer/requirements.txt`; Copilot CLI is pinned
in `.devcontainer/devcontainer.json`.

## Safety model

The configured workspace and Copilot instructions are guardrails, not an
authorization boundary. Fabric RBAC must grant write access only where each
participant is expected to work.

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
| `.cockpit/workshop.json` | Single source of workshop-specific configuration |
| `.devcontainer/` | Codespaces image, installation, authentication, and verification |
| `.github/copilot-instructions.md` | Reusable mutation guardrails |
| `.vscode/` | Participant tasks and editor defaults |
| `examples/` | Example workshop profiles |
| `guidance/` | Organizer and participant safety guidance |
| `tests/` | Configuration and exact-workspace verification tests |

## Updating dependencies

Review pinned Fabric CLI and Copilot CLI versions monthly and before every
event. Update one tool at a time, open a pull request, allow both validation
workflows to pass, then complete the clean-Codespace acceptance test before
merging. Rebuild Codespaces prebuilds after any devcontainer change.
