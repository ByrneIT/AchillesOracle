import os
import requests
from typing import Optional, Any

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")


def fetch_secret(path: str) -> Optional[Any]:
    """Fetch a secret from HashiCorp Vault KV v2 at `secret/data/{path}`.

    Returns the value payload or None on error.
    Requires `VAULT_ADDR` and `VAULT_TOKEN` environment variables.
    """
    if not VAULT_ADDR or not VAULT_TOKEN:
        return None

    url = f"{VAULT_ADDR.rstrip('/')}/v1/secret/data/{path}"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("data")
    except Exception:
        return None
