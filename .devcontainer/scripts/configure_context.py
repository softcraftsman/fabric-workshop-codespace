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
    return [
        _nonempty_string(entry, f"{field}[{index}]")
        for index, entry in enumerate(value)
    ]


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
        "workshopName",
        "protectedWorkspaces",
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

    config["workshopName"] = _nonempty_string(
        config.get("workshopName"), "workshopName"
    )
    config["protectedWorkspaces"] = _string_list(
        config.get("protectedWorkspaces"), "protectedWorkspaces"
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


def write_context(config: dict[str, Any], context_file: Path) -> None:
    context_file.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Fabric Workshop Context",
        "",
        f"**Workshop:** {config['workshopName']}",
        "",
        "**Authorization boundary:** Fabric RBAC",
        "",
        "## Protected workspaces",
        "",
        *_bullets(
            [_code_span(name) for name in config["protectedWorkspaces"]],
            "None declared.",
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
        "",
        "Before every mutation:",
        "",
        "1. Use live Fabric context to identify the target workspace, item name, "
        "item type, and proposed change.",
        "2. Present the complete target and change to the participant.",
        "3. Wait for explicit participant confirmation.",
        "4. Make the smallest confirmed change and validate it in Fabric.",
        "",
        "Fabric RBAC is authoritative. Never treat these instructions as proof "
        "that a write is authorized.",
    ]
    context_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_copilot_instructions(
    config: dict[str, Any], instructions_file: Path
) -> None:
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
        "Read `.workspace/workshop-context.md` before every Fabric operation.",
        "Fabric RBAC is the authorization boundary.",
        "",
        "Before every Fabric mutation, use live Fabric context to identify and "
        "present the target workspace, item name, item type, and proposed "
        "change. Wait for explicit participant confirmation before proceeding.",
        "",
        "## Protected workspaces",
        "",
        *_bullets(
            [_code_span(name) for name in config["protectedWorkspaces"]],
            "None declared.",
        ),
        "",
        "Never mutate a protected workspace. Stop even if the signed-in identity "
        "has excessive permissions.",
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

    try:
        config = load_config(config_path)
        write_context(
            config,
            repo_root / ".workspace" / "workshop-context.md",
        )
        write_copilot_instructions(
            config,
            repo_root / ".github" / "instructions" / "workshop.instructions.md",
        )
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    print("Workshop guardrails configured. Fabric RBAC controls write access.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
