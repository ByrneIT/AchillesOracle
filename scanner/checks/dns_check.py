import dns.resolver

def run_check(target_url):
    name = "DNS Resolution Check"

    try:
        hostname = target_url.replace("https://", "").replace("http://", "").split("/")[0]

        answers = dns.resolver.resolve(hostname, 'A')
        ips = [rdata.address for rdata in answers]

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": f"Resolved to: {', '.join(ips)}",
            "recommendation": "No action needed."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "DNS resolution failed. Check domain configuration."
        }
