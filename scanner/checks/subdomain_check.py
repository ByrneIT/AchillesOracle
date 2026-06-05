import requests

def run_check(target_url):
    name = "Subdomain Enumeration (CT Logs)"

    try:
        # Extract domain
        domain = (
            target_url.replace("https://", "")
                      .replace("http://", "")
                      .split("/")[0]
        )

        # Remove port if present
        if ":" in domain:
            domain = domain.split(":")[0]

        # Query crt.sh for certificate transparency logs
        url = f"https://crt.sh/?q=%25.{domain}&output=json"

        response = requests.get(url, timeout=8)

        if response.status_code != 200:
            return {
                "name": name,
                "status": "error",
                "severity": "high",
                "details": f"crt.sh returned status {response.status_code}",
                "recommendation": "Try again later or verify domain availability."
            }

        try:
            data = response.json()
        except Exception:
            return {
                "name": name,
                "status": "error",
                "severity": "high",
                "details": "Unable to parse JSON from crt.sh",
                "recommendation": "Try again later."
            }

        # Extract subdomains
        subdomains = set()

        for entry in data:
            name_value = entry.get("name_value", "")
            for line in name_value.split("\n"):
                if line.endswith(domain):
                    subdomains.add(line.strip())

        subdomains = sorted(subdomains)

        if not subdomains:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "No subdomains found in certificate transparency logs.",
                "recommendation": "No action needed."
            }

        return {
            "name": name,
            "status": "warn",
            "severity": "medium",
            "details": f"Discovered subdomains: {', '.join(subdomains)}",
            "recommendation": "Review exposed subdomains and ensure unused ones are removed."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to enumerate subdomains."
        }
