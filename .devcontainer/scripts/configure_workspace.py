#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    result = []
    for index, entry in enumerate(value):
        result.append(_nonempty_string(entry, f"{field}[{index}]"))
    return result


def load_config(config_path: Path) -> dict[str, Any]:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Workshop configuration not found: {config_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid workshop configuration: {error}") from error

    expected_keys = {
        "$schema",
        "schemaVersion",
        "configured",
        "workshopName",
        "workspace",
        "dataHandlingRules",
        "additionalInstructions",
    }
    unexpected_keys = set(config) - expected_keys
    if unexpected_keys:
        raise ValueError(
            f"Unexpected configuration fields: {', '.join(sorted(unexpected_keys))}"
        )
    if config.get("schemaVersion") != 1:
        raise ValueError("schemaVersion must be 1")
    if not isinstance(config.get("configured"), bool):
        raise ValueError("configured must be true or false")

    config["workshopName"] = _nonempty_string(
        config.get("workshopName"), "workshopName"
    )
    workspace = config.get("workspace")
    if not isinstance(workspace, dict):
        raise ValueError("workspace must be an object")
    expected_workspace_keys = {
        "namePattern",
        "namePatternDescription",
        "protectedWorkspaces",
    }
    unexpected_workspace_keys = set(workspace) - expected_workspace_keys
    if unexpected_workspace_keys:
        raise ValueError(
            "Unexpected workspace fields: "
            + ", ".join(sorted(unexpected_workspace_keys))
        )

    workspace["namePattern"] = _nonempty_string(
        workspace.get("namePattern"), "workspace.namePattern"
    )
    workspace["namePatternDescription"] = _nonempty_string(
        workspace.get("namePatternDescription"),
        "workspace.namePatternDescription",
    )
    try:
        re.compile(workspace["namePattern"])
    except re.error as error:
        raise ValueError(f"workspace.namePattern is invalid: {error}") from error

    workspace["protectedWorkspaces"] = _string_list(
        workspace.get("protectedWorkspaces"), "workspace.protectedWorkspaces"
    )
    config["dataHandlingRules"] = _string_list(
        config.get("dataHandlingRules"), "dataHandlingRules"
    )
    config["additionalInstructions"] = _string_list(
        config.get("additionalInstructions"), "additionalInstructions"
    )
    return config


def _code_span(value: str) -> str:
    longest_run = max((len(run) for run in re.findall(r"`+", value)), default=0)
    fence = "`" * (longest_run + 1)
    padding = " " if value.startswith("`") or value.endswith("`") else ""
    return f"{fence}{padding}{value}{padding}{fence}"


def _bullets(values: list[str], empty_text: str) -> list[str]:
    if not values:
        return [f"- {empty_text}"]
    return [f"- {value}" for value in values]


def configure_workspace(
    config: dict[str, Any], context_dir: Path, raw_workspace_name: str
) -> str:
    context_dir.mkdir(parents=True, exist_ok=True)
    context_file = context_dir / "team-context.md"
    name_file = context_dir / "team-workspace-name"
    workspace_name = raw_workspace_name.strip()
    protected = config["workspace"]["protectedWorkspaces"]

    if not workspace_name:
        name_file.unlink(missing_ok=True)
        status = (
            "UNCONFIGURED"
            if config["configured"]
            else "ORGANIZER SETUP REQUIRED"
        )
        lines = [
            "# Fabric Workshop Context",
            "",
            f"**Workshop:** {config['workshopName']}",
            "",
            f"**Status:** {status}",
            "",
        ]
        if config["configured"]:
            lines.extend(
                [
                    "Run **Codespace: Configure team workspace** before asking "
                    "Copilot to create or modify a Fabric item.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "The organizer must customize `.codespace/workshop.json` and "
                    "set `configured` to `true` before participant use.",
                    "",
                ]
            )
        lines.extend(["## Protected workspaces", ""])
        lines.extend(
            _bullets(
                [_code_span(name) for name in protected],
                "None declared; organizer configuration is incomplete.",
            )
        )
        context_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return status

    if not config["configured"]:
        raise ValueError(
            "Organizer setup is incomplete. Customize .codespace/workshop.json "
            "and set configured to true."
        )
    if "\n" in workspace_name or "\r" in workspace_name:
        raise ValueError("Workspace name must be a single line")
    if not re.fullmatch(config["workspace"]["namePattern"], workspace_name):
        raise ValueError(config["workspace"]["namePatternDescription"])
    if workspace_name.casefold() in {name.casefold() for name in protected}:
        raise ValueError(
            f"{workspace_name} is protected and cannot be configured as writable"
        )

    name_file.write_text(workspace_name + "\n", encoding="utf-8")
    lines = [
        "# Fabric Workshop Context",
        "",
        f"**Workshop:** {config['workshopName']}",
        "",
        f"**Writable workspace:** {_code_span(workspace_name)}",
        "",
        "## Protected workspaces",
        "",
    ]
    lines.extend(
        _bullets(
            [_code_span(name) for name in protected],
            "None declared.",
        )
    )
    lines.extend(
        [
            "",
            "## Data-handling rules",
            "",
            *_bullets(config["dataHandlingRules"], "No additional rules declared."),
            "",
            "## Workshop instructions",
            "",
            *_bullets(
                config["additionalInstructions"],
                "No additional instructions declared.",
            ),
            "",
            "Before any mutation, state the writable workspace, item name, item "
            "type, and proposed change. Fabric Explorer or Fabric CLI must confirm "
            "the intended workspace and signed-in identity.",
        ]
    )
    context_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return workspace_name


def write_copilot_instructions(config: dict[str, Any], instructions_file: Path) -> None:
    instructions_file.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        'applyTo: "**"',
        "---",
        "",
        "# Active Fabric Workshop Guardrails",
        "",
        f"Workshop: **{config['workshopName']}**",
        "",
        "Read `.workspace/team-context.md` before every Fabric operation. Stop "
        "unless it names a writable workspace.",
        "",
        "## Protected workspaces",
        "",
        *_bullets(
            [_code_span(name) for name in config["workspace"]["protectedWorkspaces"]],
            "None declared. Stop because organizer configuration is incomplete."
            if not config["configured"]
            else "None declared.",
        ),
        "",
        "## Data-handling rules",
        "",
        *_bullets(config["dataHandlingRules"], "No additional rules declared."),
        "",
        "## Workshop instructions",
        "",
        *_bullets(
            config["additionalInstructions"],
            "No additional instructions declared.",
        ),
    ]
    instructions_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    configured_path = os.environ.get(
        "CODESPACE_CONFIG", ".codespace/workshop.json"
    )
    config_path = Path(configured_path)
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    workspace_name = sys.argv[1] if len(sys.argv) > 1 else ""

    try:
        config = load_config(config_path)
        result = configure_workspace(config, repo_root / ".workspace", workspace_name)
        write_copilot_instructions(
            config,
            repo_root / ".github" / "instructions" / "workshop.instructions.md",
        )
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    if workspace_name.strip():
        print(f"Configured writable Fabric workspace: {result}")
    else:
        print(f"Workspace context status: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
