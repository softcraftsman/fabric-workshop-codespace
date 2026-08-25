# Organizer Setup

## Create and configure the workshop repository

1. Create a private repository from this template.
2. Edit `.codespace/workshop.json`.
3. Declare every governed or shared workspace in `protectedWorkspaces`.
4. Restrict `namePattern` when team workspace names follow a known convention.
5. Add workshop-specific data-handling rules and instructions.
6. Set `configured` to `true` only after reviewing the complete configuration.
7. Require pull-request review for configuration, devcontainer, workflow, and
   Copilot-instruction changes.

The Codespace setup generates `.workspace/team-context.md` from this one file. Do not
duplicate workshop names or protected workspace lists in scripts or Copilot
instructions.

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
4. Configure the exact assigned workspace.
5. Sign into Fabric Explorer and Fabric CLI with the same participant identity.
6. Run **Fabric CLI: Verify configured workspace**.
7. Confirm only the intended workspace is writable.
8. Use Fabric MCP to inspect a supported item schema.
9. Open or create a disposable participant-owned item.
10. Have Copilot inspect, propose, and apply a reviewed change.
11. Save and execute or refresh the item in Fabric.
12. Validate the workshop's required notebook, model, report, or ontology tools.
13. Confirm governed workspaces reject write operations.
14. Delete the disposable item and rebuild the prebuild if configuration
    changed.

## Dependency maintenance

Fabric CLI and Copilot CLI are pinned for reproducibility. Review their
upstream releases monthly and two weeks before an event. Update pins through a
pull request, allow the fast and devcontainer validation workflows to pass, and
repeat the participant-equivalent acceptance test. Extension identifiers are
validated automatically, but Marketplace extensions update through the
Codespaces prebuild and require the same acceptance test.

The weekly devcontainer workflow is disabled unless the repository variable
`ENABLE_SCHEDULED_DEVCONTAINER_CHECK` is `true`. Enable it on the maintained
upstream template; leave it disabled on short-lived workshop repositories.

## Devcontainer scripts

| Script | Purpose |
|---|---|
| `post-create.sh` | Creates the virtual environment, installs pinned CLIs, initializes context, and verifies tooling. |
| `configure-workspace.sh` | Generates participant context from `.codespace/workshop.json` and the assigned workspace name. |
| `verify-environment.sh` | Confirms required command-line tools and generated context. |
| `verify-extensions.sh` | Confirms required VS Code extensions after the editor connects. |
| `fabric-device-login.sh` | Provides an interactive device-code fallback without persisting tokens in the repository. |
| `verify-live-workspace.sh` | Resolves the exact configured workspace and verifies the returned display name and stable ID. |
