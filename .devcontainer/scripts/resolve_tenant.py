#!/usr/bin/env python3
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


GUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}$",
    re.IGNORECASE,
)
AUTHORITY_PATTERN = re.compile(
    r"^https://login\.microsoftonline\.com/"
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12})/",
    re.IGNORECASE,
)


def normalize_domain(value: str) -> str:
    value = value.strip().lower()
    if "@" in value:
        local_part, separator, domain = value.rpartition("@")
        if not separator or not local_part:
            raise ValueError("Enter a valid work email or tenant domain.")
        value = domain

    if GUID_PATTERN.fullmatch(value):
        return value
    if not DOMAIN_PATTERN.fullmatch(value):
        raise ValueError(
            "Enter a valid work email or tenant domain, such as "
            "name@contoso.com or contoso.com."
        )
    return value


def tenant_id_from_metadata(metadata: dict) -> str:
    authorization_endpoint = metadata.get("authorization_endpoint")
    if not isinstance(authorization_endpoint, str):
        raise ValueError("Tenant metadata has no authorization endpoint.")

    match = AUTHORITY_PATTERN.match(authorization_endpoint)
    if not match:
        raise ValueError(
            "This workshop supports commercial Microsoft Entra tenants only."
        )
    return match.group(1).lower()


def resolve_tenant_id(value: str) -> str:
    domain = normalize_domain(value)
    if GUID_PATTERN.fullmatch(domain):
        return domain

    url = (
        "https://login.microsoftonline.com/"
        f"{quote(domain, safe='.')}/.well-known/openid-configuration"
    )
    with urlopen(url, timeout=15) as response:
        return tenant_id_from_metadata(json.load(response))


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <work-email-or-domain>", file=sys.stderr)
        return 2

    try:
        print(resolve_tenant_id(sys.argv[1]))
    except (ValueError, HTTPError, URLError, json.JSONDecodeError) as error:
        print(f"Unable to resolve Microsoft Entra tenant: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
