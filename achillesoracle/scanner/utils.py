import time
from typing import Optional, Callable

import requests
import dns.resolver
from requests.exceptions import RequestException


def make_result(name, status, severity, details, recommendation):
    return {
        "name": name,
        "status": status,
        "severity": severity,
        "details": details,
        "recommendation": recommendation
    }


def safe_get(url: str, timeout: int = 8, max_retries: int = 2, backoff: float = 0.5, allowed_statuses: Optional[list] = None, **kwargs):
    """Perform an HTTP GET with retries and soft-fail semantics.

    Returns the Response on success, or None on network failure. Callers
    should treat non-200/allowed-status responses as non-fatal and handle
    them appropriately.
    """
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=timeout, **kwargs)
            # Return the response so callers can inspect status codes/body
            return resp
        except RequestException:
            if attempt + 1 >= max_retries:
                return None
            time.sleep(backoff * (2 ** attempt))
    return None


def safe_resolve(name: str, rdtype: str = "DNSKEY", lifetime: float = 5.0):
    """Resolve DNS records with clear return values for common outcomes.

    - Returns a list of answers when records exist
    - Returns empty list when resolver explicitly has NoAnswer (record absent)
    - Returns None when a network/error prevents resolution
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = lifetime
        resolver.lifetime = lifetime
        answers = resolver.resolve(name, rdtype)
        return list(answers)
    except dns.resolver.NoAnswer:
        return []
    except Exception:
        return None


def safe_call(fn: Callable, *args, default=None, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default
