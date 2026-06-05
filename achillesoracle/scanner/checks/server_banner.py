import requests

def run_check(target_url):
    name = "Server Banner Check"

    try:
        response = requests.get(target_url, timeout=5)
        server = response.headers.get("Server", "Unknown")

        if server == "Unknown":
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "Server header not exposed.",
                "recommendation": "No action needed."
            }

        return {
            "name": name,
            "status": "warn",
            "severity": "medium",
            "details": f"Server header exposed: {server}",
            "recommendation": "Hide or minimize server version information."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to check server banner."
        }
