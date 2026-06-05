import requests

def run_check(target_url):
    name = "Security Headers Check"

    try:
        response = requests.get(target_url, timeout=5)
        headers = response.headers

        important_headers = {
            "Strict-Transport-Security": "Missing HSTS header",
            "Content-Security-Policy": "Missing CSP header",
            "X-Frame-Options": "Missing clickjacking protection",
            "X-Content-Type-Options": "Missing MIME sniffing protection",
            "Referrer-Policy": "Missing referrer policy",
            "Permissions-Policy": "Missing permissions policy"
        }

        missing = [h for h in important_headers if h not in headers]

        if missing:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": f"Missing headers: {', '.join(missing)}",
                "recommendation": "Add missing security headers to improve protection."
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": "All important security headers are present.",
            "recommendation": "No action needed."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to check security headers."
        }
