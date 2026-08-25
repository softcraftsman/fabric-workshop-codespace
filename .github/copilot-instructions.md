# Fabric Workshop Codespace

This Codespace is a control surface for live, participant-owned Microsoft
Fabric items. Fabric remains the runtime, collaboration surface, and security
boundary.

Before any Fabric operation:

1. Read `.workspace/team-context.md`.
2. Stop if its status is `ORGANIZER SETUP REQUIRED` or `UNCONFIGURED`.
3. Use only the configured writable workspace.
4. Confirm the exact workspace through Fabric Explorer or Fabric CLI.
5. State the target workspace, item name, item type, and proposed change.
6. Begin with inspection and planning; wait for user confirmation before
   mutation.

Never create, update, move, publish, or delete items in a protected workspace
listed in `.workspace/team-context.md`. Permissions, not these instructions,
are the authoritative security boundary.

Use Fabric MCP for API specifications, item schemas, and implementation
guidance. Use Fabric Explorer or Fabric CLI for live workspace discovery.

When a supported Fabric item definition is opened in VS Code:

- Explain inputs, outputs, bindings, grain, and runtime assumptions first.
- Make the smallest approved change.
- Review the definition before saving because saving may update the live item.
- Validate execution, bindings, refresh, visuals, and semantic behavior in
  Fabric.

Follow every data-handling rule and workshop instruction in
`.workspace/team-context.md`. Never place credentials, tokens, connection
strings, or sensitive data in Copilot prompts, terminal logs, or repository
files.
