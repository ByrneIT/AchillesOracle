import requests

def run_check(target_url):
    name = "Content Security Policy Check"

    try:
        response = requests.get(target_url, timeout=5)
        csp = response.headers.get("Content-Security-Policy")

        # No CSP at all
        if not csp:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": "No Content-Security-Policy header present.",
                "recommendation": (
                    "Add a Content-Security-Policy header to mitigate XSS and content injection risks."
                )
            }

        issues = []

        csp_lower = csp.lower()

        # Dangerous keywords
        if "unsafe-inline" in csp_lower:
            issues.append("Uses 'unsafe-inline' (allows inline scripts).")
        if "unsafe-eval" in csp_lower:
            issues.append("Uses 'unsafe-eval' (allows eval-like behavior).")

        # Wildcards
        if "*" in csp and "'none'" not in csp_lower:
            issues.append("Uses wildcard '*' in CSP (overly permissive).")
        if "https://*" in csp_lower:
            issues.append("Uses 'https://*' which is still very broad.")

        # Missing key directives
        if "script-src" not in csp_lower and "default-src" not in csp_lower:
            issues.append("Missing 'script-src' and 'default-src' directives.")

        if issues:
            details = "CSP present but with weaknesses: " + " ".join(issues)
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": details,
                "recommendation": (
                    "Tighten the CSP policy: remove unsafe-inline/unsafe-eval, avoid wildcards, "
                    "and define explicit script-src/default-src."
                )
            }

        # If we got here, CSP exists and looks reasonably strict
        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": "Content-Security-Policy header present with no obvious weak patterns detected.",
            "recommendation": "Review CSP periodically as the application evolves."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to evaluate CSP. Check server availability and configuration."
        }
