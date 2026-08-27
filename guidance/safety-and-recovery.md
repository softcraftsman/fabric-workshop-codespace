# Safety and Recovery

## Permission boundary

The organizer must grant participants the least Fabric access needed:

| Resource | Typical participant permission |
|---|---|
| Assigned workspace | Contributor |
| Approved shared semantic models | Build |
| Approved shared data and ontology resources | Read |
| Governed or integration workspaces | No write access |

Copilot instructions and the configured workspace are guardrails. They cannot
override excessive Fabric permissions.

## Authentication

Use interactive participant authentication. If normal Fabric CLI login cannot
complete in a browser-hosted Codespace, use the device-code task. It obtains
temporary Fabric, OneLake, and Azure tokens and exports them only to the
interactive shell it opens. The task verifies the configured workspace before
opening that shell. Run subsequent Fabric CLI commands in the same shell;
other VS Code task terminals do not inherit its temporary tokens.

Because the Codespace has no OS keyring, setup enables Fabric CLI's supported
plaintext encryption fallback for tokens saved by normal `fab auth login`.
Treat the Codespace as credential-bearing: stop or delete it after the workshop
and never copy its Fabric CLI configuration into the repository.

Do not distribute service-principal secrets through the Codespace. If CLI
authentication remains unavailable, use Fabric Explorer for live discovery
and item access.

## Live-edit precautions

Before a substantial change:

1. Confirm the exact item and workspace.
2. Duplicate the participant-owned item or export its definition.
3. Record the observed baseline.
4. Ask Copilot for the smallest change.
5. Review before saving.
6. Validate immediately in Fabric.

Keep destructive CLI operations out of participant tasks. Never ask Copilot to
clean up a workspace broadly.

## Data handling

Follow the rules generated into `.workspace/team-context.md`. At minimum:

- Do not place credentials, tokens, connection strings, or sensitive data in
  Copilot prompts, terminal logs, or repository files.
- Use synthetic, public, aggregate, or explicitly approved data.
- Do not download restricted data into a Codespace.

## Recovery

The Fabric workspace is the durable solution location. Without Fabric Git
integration there is no automatic source rollback. Use item duplication or
definition exports for checkpoints and preserve reviewed outputs in the
organizer-designated integration location.

Codespace deletion does not delete saved Fabric items, but it deletes
unexported local scratch files and generated workspace context.
