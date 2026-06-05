import requests

def run_check(target_url):
    name = "X-Content-Type-Options Check"

    try:
        response = requests.get(target_url, timeout=6)
        headers = response.headers

        xcto = headers.get("X-Content-Type-Options")

        # Missing header
        if not xcto:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": "X-Content-Type-Options header is missing.",
                "recommendation": (
                    "Add X-Content-Type-Options: nosniff to prevent MIME type sniffing."
                )
            }

        # Normalize
        xcto_lower = xcto.lower().strip()

        # Correct configuration
        if xcto_lower == "nosniff":
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": f"X-Content-Type-Options: {xcto}",
                "recommendation": "MIME sniffing protection is correctly configured."
            }

        # Incorrect or unknown value
        return {
            "name": name,
            "status": "warn",
            "severity": "medium",
            "details": f"Unrecognized X-Content-Type-Options value: {xcto}",
            "recommendation": (
                "Use X-Content-Type-Options: nosniff for proper MIME type protection."
            )
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to evaluate X-Content-Type-Options."
        }
