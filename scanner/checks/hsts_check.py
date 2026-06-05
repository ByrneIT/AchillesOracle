import requests

def run_check(target_url):
    name = "HSTS (Strict-Transport-Security) Analysis"

    try:
        response = requests.get(target_url, timeout=6)
        headers = response.headers

        hsts = headers.get("Strict-Transport-Security")

        # If no HSTS header at all
        if not hsts:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": "HSTS header is missing.",
                "recommendation": (
                    "Add Strict-Transport-Security with a strong max-age. "
                    "Example: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"
                )
            }

        # Parse HSTS
        hsts_lower = hsts.lower()

        issues = []

        # Check max-age
        max_age = None
        if "max-age=" in hsts_lower:
            try:
                max_age = int(hsts_lower.split("max-age=")[1].split(";")[0])
            except:
                issues.append("Invalid max-age value.")
        else:
            issues.append("Missing max-age directive.")

        # Check includeSubDomains
        if "includesubdomains" not in hsts_lower:
            issues.append("Missing includeSubDomains directive.")

        # Check preload
        preload = "preload" in hsts_lower

        # Build details
        details = f"HSTS header: {hsts}"

        # Classification logic
        if issues:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": details + " | Issues: " + ", ".join(issues),
                "recommendation": (
                    "Strengthen HSTS configuration. Recommended: "
                    "max-age=31536000; includeSubDomains; preload"
                )
            }

        # If everything is good but preload is missing
        if not preload:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": details,
                "recommendation": (
                    "HSTS is configured correctly. Consider adding 'preload' "
                    "if you want to submit your domain to the preload list."
                )
            }

        # Perfect configuration
        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": details,
            "recommendation": "HSTS configuration is strong and preload-ready."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to perform HSTS analysis."
        }
