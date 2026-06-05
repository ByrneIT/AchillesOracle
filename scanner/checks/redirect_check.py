import requests

def run_check(target_url):
    name = "Redirect Chain Check"

    try:
        response = requests.get(target_url, timeout=5, allow_redirects=True)
        chain = [resp.url for resp in response.history] + [response.url]

        if len(chain) > 1:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": " → ".join(chain),
                "recommendation": "Review redirect chain for unnecessary hops."
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": "No redirects detected.",
            "recommendation": "No action needed."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to check redirect chain."
        }
