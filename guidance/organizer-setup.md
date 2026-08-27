# Optional Organizer Setup

## Customize the workshop

The default configuration is ready to use. For workshop-specific guardrails:

1. Edit `.codespace/workshop.json`.
2. Declare every governed or shared workspace in `protectedWorkspaces`.
3. Add workshop-specific data-handling rules and instructions.
4. Review the complete configuration.
5. Require pull-request review for configuration, devcontainer, workflow, and
   Copilot-instruction changes.

The Codespace setup generates `.workspace/workshop-context.md` from this file.
Do not duplicate workshop names or protected workspace lists in scripts or
Copilot instructions.

Codespaces are personal environments. Participants collaborate through their
Fabric workspace, not a shared running Codespace.

## Codespaces and Copilot

1. Enable GitHub Codespaces and Copilot for the participant population.
2. Configure a Codespaces prebuild after the repository is customized.
3. Use a 2-core, 8-GB machine as the default; Fabric performs the computation.
4. Set event-appropriate inactivity and retention policies.
5. Confirm organization and Marketplace policies permit every recommended
   extension.
6. Confirm network policy allows GitHub Copilot and Microsoft Fabric service
   endpoints.

Installation does not prove entitlement or service access. Test Copilot Chat,
Agent mode, Fabric Explorer, and Fabric MCP with a participant-equivalent
GitHub identity.

## Extension rationale

| Extension | Why it is preinstalled |
|---|---|
| `GitHub.copilot` | Provides inline code completion and next-edit assistance for workshop development. |
| `GitHub.copilot-chat` | Provides the Chat and Agent interfaces that apply repository instructions and orchestrate MCP tools. |
| `fabric.vscode-fabric` | Provides Fabric sign-in, workspace and item navigation, and opening Fabric item definitions in VS Code. |
| `fabric.vscode-fabric-mcp-server` | Registers Fabric API specifications, item schemas, examples, and best practices with VS Code Copilot. Copilot CLI uses the separate repository-level `.github/mcp.json` registration. |
| `analysis-services.TMDL` | Adds syntax highlighting, completion, formatting, diagnostics, and navigation for TMDL semantic-model definitions. |
| `analysis-services.powerbi-modeling-mcp` | Enables agent-assisted inspection, validation, and modification of Power BI and Fabric semantic models. |
| `ms-python.python` | Provides Python environment selection, execution, debugging, and test integration for workshop scripts and notebooks. |
| `ms-python.vscode-pylance` | Adds Python IntelliSense, type analysis, navigation, and diagnostics on top of the Python extension. |
| `ms-toolsai.jupyter` | Provides native `.ipynb` editing, cell execution, debugging, rich output, and variable inspection. |
| `ms-mssql.mssql` | Provides connections, Object Explorer, IntelliSense, query execution, and result inspection for Fabric SQL endpoints and warehouses. |

The Fabric, Copilot Chat, and Fabric MCP extensions form the core guided
experience. TMDL, Power BI Modeling MCP, Python, Pylance, Jupyter, and MSSQL
support the corresponding workshop workloads and may be removed together with
their acceptance criteria when those workloads are explicitly out of scope.

## Fabric authorization

- Grant Contributor only on the assigned participant or team workspace.
- Grant Build or Read on approved shared resources as required.
- Do not grant participants write roles on governed workspaces.
- Prefer dedicated workshop identities if normal identities have broader
  tenant permissions than the event requires.

Codespaces cannot reduce the permissions of an existing Microsoft Entra token.
The protected-workspace configuration is a guardrail, not RBAC.

## Participant-equivalent acceptance test

1. Launch a clean Codespace from the customized repository.
2. Verify required extensions and command-line tools.
3. Confirm Copilot Chat answers a prompt and Agent mode is available.
4. Sign into Fabric Explorer and Fabric CLI with the same participant identity.
5. Confirm only the intended participant or team workspace is writable.
6. Use Fabric MCP to inspect a supported item schema.
7. Open or create a disposable participant-owned item.
8. Have Copilot identify and present the target workspace, item, item type, and
   proposed change.
9. Confirm the target, then have Copilot apply the reviewed change.
10. Save and execute or refresh the item in Fabric.
11. Validate the workshop's required notebook, model, report, or ontology tools.
12. Confirm governed workspaces reject write operations.
13. Delete the disposable item and rebuild the prebuild if configuration
    changed.

## Codespaces prebuild

Configure a prebuild before distributing the workshop repository so shared
tool installation runs once rather than for every participant:

1. Open the repository's **Settings > Codespaces > Set up prebuild**.
2. Select the workshop branch and the region nearest the participants.
3. Update the prebuild on every push while preparing the workshop.
4. Enable failure notifications and create the prebuild configuration.
5. Wait for the generated prebuild workflow to succeed.
6. Create a clean participant-equivalent Codespace from the same branch and
   region, then complete the acceptance test above.

The devcontainer's `onCreateCommand` installs the shared Python, Fabric CLI,
and Copilot CLI tooling into the prebuild. Its `postCreateCommand` performs
only fast per-participant shell, guardrail, and environment initialization.
Rebuild the prebuild after changing the devcontainer, tool versions, or setup
scripts.

## Dependency maintenance

Fabric CLI is pinned for reproducibility. Copilot CLI and Fabric MCP track
their latest npm releases when the Codespaces prebuild runs. Review upstream
releases monthly and two weeks before an event. Update the Fabric CLI pin
through a pull request when required, allow the fast and devcontainer
validation workflows to pass, and repeat the participant-equivalent acceptance
test. Rebuild and test the prebuild before an event to validate the Copilot CLI
and Fabric MCP versions resolved by `@latest`. Extension identifiers are
validated automatically, but Marketplace extensions update through the
Codespaces prebuild and require the same acceptance test.

The weekly devcontainer workflow is disabled unless the repository variable
`ENABLE_SCHEDULED_DEVCONTAINER_CHECK` is `true`. Enable it when this repository
should receive regular dependency checks.

## Devcontainer scripts

| Script | Purpose |
|---|---|
| `install-tools.sh` | Installs the pinned Fabric CLI and latest npm-based shared tooling during image creation or prebuild. |
| `post-create.sh` | Initializes participant-specific shell, Copilot trust, workshop context, and environment checks. |
| `configure-shell.sh` | Loads shared Fabric authentication in new terminals and trusts only the workshop repository in Copilot CLI. |
| `configure-context.sh` | Generates workshop guardrails from `.codespace/workshop.json`. |
| `verify-environment.sh` | Confirms required command-line tools and generated context. |
| `verify-extensions.sh` | Confirms required VS Code extensions after the editor connects. |
| `fabric-login.sh` | Resolves a participant's tenant from their work email or domain and opens an authenticated Fabric CLI shell. |
