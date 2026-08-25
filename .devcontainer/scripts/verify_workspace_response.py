#!/usr/bin/env python3
import json
import sys
from typing import Any


def exact_workspace(response: dict[str, Any], expected_name: str) -> tuple[str, str]:
    if response.get("status") != "Success":
        raise ValueError("Fabric CLI did not return a successful response")

    result = response.get("result")
    if not isinstance(result, dict):
        raise ValueError("Fabric CLI response has no result object")
    data = result.get("data")
    if isinstance(data, list):
        if len(data) != 1:
            raise ValueError("Fabric CLI response did not identify one workspace")
        data = data[0]
    if not isinstance(data, dict):
        raise ValueError("Fabric CLI response has no workspace data")

    actual_name = data.get("displayName", data.get("name"))
    if actual_name != expected_name:
        raise ValueError(
            f"Fabric CLI resolved {actual_name!r}, not {expected_name!r}"
        )
    workspace_id = data.get("id")
    if not isinstance(workspace_id, str) or not workspace_id:
        raise ValueError("Fabric CLI response has no workspace ID")
    return actual_name, workspace_id


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: verify_workspace_response.py <workspace-name>", file=sys.stderr)
        return 2
    try:
        response = json.load(sys.stdin)
        name, workspace_id = exact_workspace(response, sys.argv[1])
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Workspace verification failed: {error}", file=sys.stderr)
        return 1
    print(f"Verified exact Fabric workspace: {name} ({workspace_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
