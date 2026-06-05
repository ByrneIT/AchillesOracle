import requests
from urllib.parse import urlparse, parse_qs

SSRF_PARAMS = [
    "url",
    "uri",
    "path",
    "fetch",
    "proxy",
    "load",
    "resource",
    "file",
    "endpoint",
    "api",
    "target",
    "callback",
]

def run_check(target_url):
    name = "SSRF Parameter Detection"

    try:
        parsed = urlparse(target_url)
        query = parse_qs(parsed.query)

        findings = []
        issues = []

        for param in SSRF_PARAMS:
            if param in query:
                value = query[param][0]
                findings.append(f"{param}={value}")

                # If the value looks like a URL, that's a red flag
                if value.startswith("http://") or value.startswith("https://"):
                    issues.append(f"Parameter '{param}' contains a full URL (potential SSRF vector).")

                # If the value references localhost or internal IPs
                if "127.0.0.1" in value or "localhost" in value or "169.254" in value:
                    issues.append(f"Parameter '{param}' references internal resources.")

        if not findings:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "No SSRF-like parameters detected.",
                "recommendation": "No action needed."
            }

        details = " | ".join(findings)

        if issues:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": details + " | Issues: " + ", ".join(issues),
                "recommendation": (
                    "Avoid exposing user-controlled parameters that fetch remote resources. "
                    "Validate against an allowlist and restrict internal network access."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": details,
            "recommendation": "SSRF-like parameters detected but no obvious risks found."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to analyze SSRF patterns."
        }
