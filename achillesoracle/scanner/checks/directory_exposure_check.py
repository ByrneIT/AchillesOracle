import requests

def run_check(target_url):
    name = "Directory and File Exposure Check"

    # High‑risk paths to test
    paths = [
        "/.git/",
        "/.env",
        "/config/",
        "/backup/",
        "/backups/",
        "/admin/",
        "/admin.php",
        "/phpinfo.php",
        "/server-status",
        "/test/",
        "/dev/",
        "/staging/",
        "/wp-admin/",
        "/wp-json/",
        "/logs/",
        "/private/",
        "/tmp/",
        "/uploads/",
    ]

    exposed = []

    try:
        for p in paths:
            url = target_url.rstrip("/") + p
            try:
                r = requests.get(url, timeout=4, allow_redirects=True)

                # If the server returns 200 OK, 403 Forbidden, or directory listing
                if r.status_code in (200, 403):
                    # 403 means the directory exists but is protected — still interesting
                    exposed.append(f"{p} (HTTP {r.status_code})")

            except Exception:
                continue

        if exposed:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": "Exposed or sensitive paths detected: " + ", ".join(exposed),
                "recommendation": (
                    "Restrict access to these paths or remove them if unused. "
                    "Ensure no sensitive files or directories are publicly accessible."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": "No common sensitive directories or files were exposed.",
            "recommendation": "No action needed."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to perform directory exposure checks."
        }
