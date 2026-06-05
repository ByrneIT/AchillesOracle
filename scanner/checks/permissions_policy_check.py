import requests

def run_check(target_url):
    name = "Permissions-Policy Check"

    try:
        response = requests.get(target_url, timeout=6)
        headers = response.headers

        policy = headers.get("Permissions-Policy") or headers.get("Feature-Policy")

        # Missing header entirely
        if not policy:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": "Permissions-Policy header is missing.",
                "recommendation": (
                    "Add a Permissions-Policy header to restrict powerful browser features. "
                    "Example: Permissions-Policy: camera=(), microphone=(), geolocation=()"
                )
            }

        # Normalize
        p = policy.lower()

        issues = []

        # Detect wildcards
        if "*" in p:
            issues.append("Permissions-Policy contains wildcard (*), allowing all origins.")

        # Detect insecure HTTP origins
        if "http://" in p:
            issues.append("Permissions-Policy allows insecure (HTTP) origins.")

        # Detect deprecated Feature-Policy usage
        if "feature-policy" in headers:
            issues.append("Using deprecated Feature-Policy header; replace with Permissions-Policy.")

        # Result logic
        if issues:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": f"Permissions-Policy: {policy} | Issues: {', '.join(issues)}",
                "recommendation": (
                    "Use restrictive Permissions-Policy values. "
                    "Example: camera=(), microphone=(), geolocation=()"
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": f"Permissions-Policy: {policy}",
            "recommendation": "Permissions-Policy appears correctly configured."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to evaluate Permissions-Policy."
        }

