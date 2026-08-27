#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from typing import Any


def add_trusted_folder(config_path: Path, folder: Path) -> bool:
    config: dict[str, Any] = {}
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid Copilot CLI configuration: {error}") from error
        if not isinstance(loaded, dict):
            raise ValueError("Copilot CLI configuration must be a JSON object.")
        config = loaded

    trusted_folders = config.get("trustedFolders", [])
    if not isinstance(trusted_folders, list) or not all(
        isinstance(entry, str) for entry in trusted_folders
    ):
        raise ValueError("Copilot CLI trustedFolders must be an array of paths.")

    trusted_folder = str(folder.resolve())
    if trusted_folder in trusted_folders:
        return False

    config["trustedFolders"] = [*trusted_folders, trusted_folder]
    config_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary_path = config_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary_path, 0o600)
    temporary_path.replace(config_path)
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <trusted-folder>", file=sys.stderr)
        return 2

    copilot_home = Path(
        os.environ.get("COPILOT_HOME", Path.home() / ".copilot")
    )
    try:
        changed = add_trusted_folder(
            copilot_home / "config.json",
            Path(sys.argv[1]),
        )
    except (OSError, ValueError) as error:
        print(f"Unable to configure Copilot CLI trust: {error}", file=sys.stderr)
        return 1

    if changed:
        print(f"Trusted workshop folder for Copilot CLI: {Path(sys.argv[1]).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
