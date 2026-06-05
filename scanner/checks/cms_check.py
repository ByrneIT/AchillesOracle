import requests
import re

def run_check(target_url):
    name = "CMS and Framework Detection"

    try:
        response = requests.get(target_url, timeout=6)
        html = response.text.lower()
        headers = response.headers

        detected = []
        version_info = []

        # --- WORDPRESS ---
        if "wp-content" in html or "wp-includes" in html or "wordpress" in html:
            detected.append("WordPress")
            # Try version detection
            gen = re.search(r'<meta name="generator" content="wordpress\s*([0-9\.]+)"', html)
            if gen:
                version_info.append(f"WordPress version {gen.group(1)}")

        # --- JOOMLA ---
        if "joomla" in html:
            detected.append("Joomla")
            gen = re.search(r'joomla!\s*([0-9\.]+)', html)
            if gen:
                version_info.append(f"Joomla version {gen.group(1)}")

        # --- DRUPAL ---
        if "drupal" in html or "sites/default" in html:
            detected.append("Drupal")
            gen = re.search(r'drupal\s*([0-9\.]+)', html)
            if gen:
                version_info.append(f"Drupal version {gen.group(1)}")

        # --- MAGENTO ---
        if "mage-" in html or "magento" in html:
            detected.append("Magento")

        # --- GHOST ---
        if "ghost-sdk" in html or "ghost" in html:
            detected.append("Ghost CMS")

        # --- SHOPIFY ---
        if "x-shopify-stage" in headers or "shopify" in html:
            detected.append("Shopify")

        # --- WIX ---
        if "wix.com" in html or "x-wix-request-id" in headers:
            detected.append("Wix")

        # --- SQUARESPACE ---
        if "squarespace" in html:
            detected.append("Squarespace")

        # --- FRAMEWORKS ---
        if "laravel" in html or "x-powered-by" in headers and "laravel" in headers.get("x-powered-by", "").lower():
            detected.append("Laravel")

        if "django" in html:
            detected.append("Django")

        if "express" in headers.get("x-powered-by", "").lower():
            detected.append("Express.js")

        if "rails" in html:
            detected.append("Ruby on Rails")

        if "asp.net" in headers.get("x-powered-by", "").lower():
            detected.append("ASP.NET")

        # --- RESULT LOGIC ---
        if not detected:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "No recognizable CMS or framework detected.",
                "recommendation": "No action needed."
            }

        details = "Detected: " + ", ".join(detected)
        if version_info:
            details += " | Versions: " + ", ".join(version_info)

        return {
            "name": name,
            "status": "warn",
            "severity": "medium",
            "details": details,
            "recommendation": (
                "Ensure the CMS/framework is up to date and unnecessary endpoints are restricted."
            )
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to detect CMS/framework."
        }
