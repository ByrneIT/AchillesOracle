import subprocess
import re
from datetime import datetime
import dns.resolver

def run_check(target_url):
    name = "WHOIS, Domain Age, and DNSSEC Check"

    try:
        # Extract domain
        domain = (
            target_url.replace("https://", "")
                      .replace("http://", "")
                      .split("/")[0]
        )

        if ":" in domain:
            domain = domain.split(":")[0]

        # Run system whois
        try:
            result = subprocess.check_output(
                ["whois", domain],
                stderr=subprocess.STDOUT,
                timeout=8,
                text=True
            )
        except Exception as e:
            return {
                "name": name,
                "status": "error",
                "severity": "high",
                "details": f"WHOIS command failed: {e}",
                "recommendation": "Ensure the 'whois' package is installed on the system."
            }

        # Extract creation and expiration dates
        created = None
        expires = None

        created_match = re.search(r"Creation Date:\s*(.+)", result, re.IGNORECASE)
        if created_match:
            try:
                created = datetime.strptime(created_match.group(1).strip(), "%Y-%m-%dT%H:%M:%SZ")
            except:
                pass

        expires_match = re.search(r"Expiry Date:\s*(.+)", result, re.IGNORECASE)
        if not expires_match:
            expires_match = re.search(r"Expiration Date:\s*(.+)", result, re.IGNORECASE)

        if expires_match:
            try:
                expires = datetime.strptime(expires_match.group(1).strip(), "%Y-%m-%dT%H:%M:%SZ")
            except:
                pass

        now = datetime.utcnow()

        # Domain age
        age_days = (now - created).days if created else None

        # Expiration
        days_to_expire = (expires - now).days if expires else None

        # DNSSEC check
        dnssec_status = "unknown"
        try:
            answers = dns.resolver.resolve(domain, "DNSKEY")
            if answers:
                dnssec_status = "enabled"
        except dns.resolver.NoAnswer:
            dnssec_status = "disabled"
        except Exception:
            dnssec_status = "unknown"

        # Build details
        details = (
            f"Created: {created}; "
            f"Expires: {expires}; "
            f"Domain age: {age_days} days; "
            f"DNSSEC: {dnssec_status}"
        )

        # Classification
        if age_days is not None and age_days < 30:
            status = "warn"
            severity = "medium"
            recommendation = "Domain is very new. Review for potential phishing risk."
        elif days_to_expire is not None and days_to_expire < 30:
            status = "warn"
            severity = "medium"
            recommendation = "Domain expires soon. Renew to avoid service disruption."
        elif dnssec_status == "disabled":
            status = "warn"
            severity = "low"
            recommendation = "Enable DNSSEC to improve domain integrity."
        else:
            status = "pass"
            severity = "low"
            recommendation = "WHOIS and DNSSEC configuration appear normal."

        return {
            "name": name,
            "status": status,
            "severity": severity,
            "details": details,
            "recommendation": recommendation
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to perform WHOIS/DNSSEC checks."
        }
