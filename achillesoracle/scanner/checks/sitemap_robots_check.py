import requests

def fetch(url):
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return r.text
    except:
        return None
    return None

def run_check(target_url):
    name = "Sitemap & robots.txt Analyzer"

    # Normalize domain
    if target_url.endswith("/"):
        target_url = target_url[:-1]

    robots_url = target_url + "/robots.txt"
    sitemap_url = target_url + "/sitemap.xml"

    robots = fetch(robots_url)
    sitemap = fetch(sitemap_url)

    findings = []
    issues = []

    # --- robots.txt ---
    if robots:
        findings.append("robots.txt found")
        lines = robots.splitlines()

        disallowed = [l for l in lines if l.lower().startswith("disallow:")]
        allowed = [l for l in lines if l.lower().startswith("allow:")]

        if disallowed:
            findings.append(f"Disallowed paths: {', '.join(disallowed)}")

            # Flag sensitive directories
            sensitive = ["admin", "backup", "private", "staging", "test"]
            for line in disallowed:
                for s in sensitive:
                    if s in line.lower():
                        issues.append(f"Sensitive path disallowed in robots.txt: {line}")
    else:
        issues.append("robots.txt missing")

    # --- sitemap.xml ---
    if sitemap:
        findings.append("sitemap.xml found")

        # Basic check for URLs inside sitemap
        if "<loc>" not in sitemap.lower():
            issues.append("Sitemap found but contains no <loc> entries.")
    else:
        issues.append("sitemap.xml missing")

    # --- Build result ---
    details = " | ".join(findings) if findings else "No sitemap or robots.txt found."

    if issues:
        return {
            "name": name,
            "status": "warn",
            "severity": "medium",
            "details": details + " | Issues: " + ", ".join(issues),
            "recommendation": (
                "Ensure robots.txt and sitemap.xml are properly configured. "
                "Avoid exposing sensitive directories in robots.txt. "
                "Include valid <loc> entries in sitemap.xml for SEO and security clarity."
            )
        }

    return {
        "name": name,
        "status": "pass",
        "severity": "low",
        "details": details,
        "recommendation": "Sitemap and robots.txt appear correctly configured."
    }
