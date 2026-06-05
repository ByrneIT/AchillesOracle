import requests

def run_check(target_url):
    name = "Cookie Security Flags Check"

    try:
        response = requests.get(target_url, timeout=5)
        cookies = response.cookies

        if not cookies:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "No cookies were set by the server.",
                "recommendation": "No action needed."
            }

        issues = []
        cookie_details = []

        for cookie in cookies:
            c_name = cookie.name
            c_secure = cookie.secure
            c_httponly = cookie.has_nonstandard_attr("HttpOnly")
            c_samesite = cookie.get_nonstandard_attr("SameSite")
            c_domain = cookie.domain
            c_path = cookie.path

            # Collect details
            cookie_details.append(
                f"{c_name}: Secure={c_secure}, HttpOnly={c_httponly}, "
                f"SameSite={c_samesite}, Domain={c_domain}, Path={c_path}"
            )

            # Security checks
            if not c_secure:
                issues.append(f"Cookie '{c_name}' missing Secure flag.")
            if not c_httponly:
                issues.append(f"Cookie '{c_name}' missing HttpOnly flag.")
            if not c_samesite:
                issues.append(f"Cookie '{c_name}' missing SameSite attribute.")
            if c_samesite and c_samesite.lower() == "none" and not c_secure:
                issues.append(
                    f"Cookie '{c_name}' uses SameSite=None without Secure (insecure)."
                )

        if issues:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": " | ".join(cookie_details) + " | Issues: " + " ".join(issues),
                "recommendation": (
                    "Set Secure, HttpOnly, and SameSite attributes on cookies. "
                    "Avoid SameSite=None unless absolutely required and always pair it with Secure."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": " | ".join(cookie_details),
            "recommendation": "Cookie security attributes appear correctly configured."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to evaluate cookie security flags."
        }
