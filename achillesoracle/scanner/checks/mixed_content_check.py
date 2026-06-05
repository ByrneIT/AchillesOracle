import requests
import re

def run_check(target_url):
    name = "Mixed Content Detection"

    try:
        response = requests.get(target_url, timeout=6)
        html = response.text

        # Only relevant if the page is HTTPS
        if not target_url.startswith("https://"):
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "Target is not HTTPS; mixed content does not apply.",
                "recommendation": "Enable HTTPS to improve security."
            }

        # Regex to find http:// resources
        pattern = r'http://[^\s"\'<>]+'
        matches = re.findall(pattern, html, re.IGNORECASE)

        # Filter out false positives (like http://localhost)
        mixed = [
            m for m in matches
            if not m.startswith("http://localhost")
            and not m.startswith("http://127.")
            and not m.startswith("http://0.0.0.0")
        ]

        if mixed:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": "Mixed content detected: " + ", ".join(mixed[:10]) +
                           (" (and more...)" if len(mixed) > 10 else ""),
                "recommendation": (
                    "Replace HTTP resources with HTTPS equivalents. "
                    "Browsers may block these resources, causing broken functionality."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": "No mixed content detected.",
            "recommendation": "No action needed."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to perform mixed content detection."
        }
