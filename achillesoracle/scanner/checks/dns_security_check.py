import dns.resolver
from urllib.parse import urlparse

def _get_domain(target_url):
    parsed = urlparse(target_url)
    host = parsed.netloc or parsed.path
    return host.split(":")[0]

def run_check(target_url):
    name = "DNS Security (SPF / DKIM / DMARC / CAA)"
    domain = _get_domain(target_url)

    results = []
    issues = []

    try:
        # SPF
        try:
            spf_records = dns.resolver.resolve(domain, "TXT")
            spf_txt = [r.to_text().strip('"') for r in spf_records if "v=spf1" in r.to_text()]
            if not spf_txt:
                issues.append("SPF: Missing SPF record.")
            else:
                if len(spf_txt) > 1:
                    issues.append("SPF: Multiple SPF records detected (invalid).")
                results.append(f"SPF: {spf_txt[0]}")
        except Exception:
            issues.append("SPF: Unable to resolve TXT records or none found.")

        # DMARC
        try:
            dmarc_domain = f"_dmarc.{domain}"
            dmarc_records = dns.resolver.resolve(dmarc_domain, "TXT")
            dmarc_txt = [r.to_text().strip('"') for r in dmarc_records if "v=dmarc1" in r.to_text().lower()]
            if not dmarc_txt:
                issues.append("DMARC: Missing DMARC record.")
            else:
                policy = "unknown"
                txt = dmarc_txt[0].lower()
                for part in txt.split(";"):
                    part = part.strip()
                    if part.startswith("p="):
                        policy = part.split("=", 1)[1]
                results.append(f"DMARC: {dmarc_txt[0]}")
                if policy == "none":
                    issues.append("DMARC: Policy is 'none' (monitoring only).")
        except Exception:
            issues.append("DMARC: Unable to resolve DMARC TXT record.")

        # CAA
        try:
            caa_records = dns.resolver.resolve(domain, "CAA")
            caa_txt = [r.to_text() for r in caa_records]
            results.append("CAA: " + ", ".join(caa_txt))
        except Exception:
            issues.append("CAA: No CAA records found (any CA can issue certificates).")

        # DKIM (basic presence check for common selectors)
        common_selectors = ["default", "selector1", "selector2"]
        dkim_found = False
        for sel in common_selectors:
            try:
                dkim_domain = f"{sel}._domainkey.{domain}"
                dkim_records = dns.resolver.resolve(dkim_domain, "TXT")
                dkim_txt = [r.to_text().strip('"') for r in dkim_records]
                if dkim_txt:
                    results.append(f"DKIM ({sel}): {dkim_txt[0]}")
                    dkim_found = True
            except Exception:
                continue
        if not dkim_found:
            issues.append("DKIM: No DKIM records found for common selectors (may still exist under custom selectors).")

        # Build result
        details = " | ".join(results) if results else "No DNS security records detected."

        if issues:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": details + " | Issues: " + ", ".join(issues),
                "recommendation": (
                    "Configure SPF, DKIM, DMARC, and CAA to improve email security and "
                    "prevent spoofing. Use strong DMARC policies (quarantine/reject) "
                    "and define CAA records to restrict certificate authorities."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": details,
            "recommendation": "DNS security records appear correctly configured."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to perform DNS security analysis."
        }
