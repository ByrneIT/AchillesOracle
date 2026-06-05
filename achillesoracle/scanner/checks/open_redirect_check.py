import requests
from urllib.parse import urlparse, parse_qs

REDIRECT_PARAMS = [
    "redirect",
    "redirect_url",
    "redirect_uri",
    "redir",
    "url",
    "next",
    "dest",
    "destination",
    "forward",
    "goto",
    "out",
]

def run_check(target_url):
    name = "Open Redirect Pattern Detection"

    try:
        response = requests.get(target_url, timeout=8)
        parsed = urlparse(target_url)
        query = parse_qs(parsed.query)

        findings = []
        issues = []

        # Look for redirect-like parameters
        for param in REDIRECT_PARAMS:
            if param in query:
                value = query[param][0]
                findings.append(f"{param}={value}")

                # If it contains a full URL, that's a red flag
                if value.startswith("http://") or value.startswith("https://"):
                    issues.append(f"Parameter '{param}' contains a full URL (potential open redirect).")

        if not findings:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "No redirect-like parameters detected.",
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
                    "Avoid using user-controlled redirect parameters. "
                    "Validate redirect targets against an allowlist."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": details,
            "recommendation": "Redirect parameters detected but no obvious risks found."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to analyze redirect patterns."
        }
