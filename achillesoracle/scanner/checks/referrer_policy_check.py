import requests

def run_check(target_url):
    name = "Referrer-Policy Check"

    try:
        response = requests.get(target_url, timeout=6)
        headers = response.headers

        policy = headers.get("Referrer-Policy")

        # If missing entirely
        if not policy:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": "Referrer-Policy header is missing.",
                "recommendation": (
                    "Add a Referrer-Policy header to control what information is sent "
                    "in the Referer header. Recommended: 'strict-origin-when-cross-origin'."
                )
            }

        # Normalize
        p = policy.lower().strip()

        # Known safe policies
        safe = [
            "no-referrer",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "same-origin"
        ]

        # Known weaker policies
        weak = [
            "origin",
            "origin-when-cross-origin",
            "unsafe-url"
        ]

        if p in safe:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": f"Referrer-Policy: {policy}",
                "recommendation": "Referrer-Policy is strong and privacy-friendly."
            }

        if p in weak:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": f"Weak Referrer-Policy detected: {policy}",
                "recommendation": (
                    "Consider upgrading to 'strict-origin-when-cross-origin' or "
                    "'no-referrer' for improved privacy and security."
                )
            }

        # Unknown or custom policy
        return {
            "name": name,
            "status": "warn",
            "severity": "medium",
            "details": f"Unrecognized Referrer-Policy: {policy}",
            "recommendation": (
                "Ensure the Referrer-Policy is valid and intentional. "
                "Recommended: 'strict-origin-when-cross-origin'."
            )
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to evaluate Referrer-Policy."
        }
