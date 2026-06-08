from achillesoracle.scanner.utils import safe_get


def _query_crtsh(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    resp = safe_get(url, timeout=8)
    if resp is None:
        raise RuntimeError("crt.sh unreachable or timed out")
    if resp.status_code != 200:
        raise RuntimeError(f"crt.sh returned status {resp.status_code}")
    try:
        return resp.json()
    except Exception:
        raise RuntimeError("crt.sh response not valid JSON")


def _query_certspotter(domain):
    # public CertSpotter endpoint
    url = (
        f"https://api.certspotter.com/v1/issuances?domain={domain}"
        f"&include_subdomains=true&expand=dns_names"
    )
    resp = safe_get(url, timeout=8)
    if resp is None:
        raise RuntimeError("CertSpotter unreachable or timed out")
    if resp.status_code != 200:
        raise RuntimeError(f"CertSpotter returned status {resp.status_code}")
    try:
        return resp.json()
    except Exception:
        raise RuntimeError("CertSpotter response not valid JSON")


def _query_google_ct(domain):
    # Google CT public UI endpoint (best-effort). HTML responses will be treated as failures.
    url = f"https://transparencyreport.google.com/pki/ct/search?domain={domain}"
    resp = safe_get(url, timeout=8)
    if resp is None:
        raise RuntimeError("Google CT unreachable or timed out")
    if resp.status_code != 200:
        raise RuntimeError(f"Google CT returned status {resp.status_code}")
    # Google does not provide a simple JSON API here; treat as success only if content contains domain
    text = resp.text or ""
    if domain not in text:
        raise RuntimeError("Google CT response did not contain domain details")
    # Return minimal data so caller can detect presence
    return [{"name_value": domain}]


def run_check(target_url):
    name = "Subdomain Enumeration (CT Logs)"

    # Extract domain
    domain = (
        target_url.replace("https://", "")
                  .replace("http://", "")
                  .split("/")[0]
    )

    # Remove port if present
    if ":" in domain:
        domain = domain.split(":")[0]

    sources = [
        ("crt.sh", _query_crtsh),
        ("certspotter", _query_certspotter),
        ("google_ct", _query_google_ct),
    ]

    last_err = None
    subdomains = set()
    used_source = None

    for label, fn in sources:
        try:
            data = fn(domain)
            # normalize entries
            for entry in (data or []):
                if isinstance(entry, dict):
                    name_value = entry.get(
                        "name_value") or entry.get("dns_names")
                else:
                    name_value = None

                if not name_value:
                    # certspotter returns objects with 'dns_names' list
                    if isinstance(entry, dict) and "dns_names" in entry:
                        for n in entry.get("dns_names") or []:
                            if n and n.endswith(domain):
                                subdomains.add(n.strip())
                        continue
                    continue

                # name_value can be a newline-separated string
                if isinstance(name_value, list):
                    candidates = name_value
                else:
                    candidates = str(name_value).split("\n")

                for line in candidates:
                    ln = line.strip()
                    if ln and ln.endswith(domain):
                        subdomains.add(ln)

            if subdomains:
                used_source = label
                break
            else:
                # If the source returned successfully but no subdomains, it's a valid pass
                used_source = label
                break

        except Exception as e:
            last_err = e
            # try next source
            continue

    if used_source is None:
        # All sources failed due to network/API issues -> soft-fail/neutral
        return {
            "name": name,
            "status": "soft-fail",
            "severity": "low",
            "details": f"All CT sources failed: {last_err}",
            "recommendation": "Certificate transparency sources unavailable; treating as neutral (soft-fail)."
        }

    # If we reached here, used_source is set. If no subdomains discovered, return pass.
    if not subdomains:
        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": f"No subdomains found in {used_source}.",
            "recommendation": "No action needed."
        }

    # Found subdomains
    return {
        "name": name,
        "status": "warn",
        "severity": "medium",
        "details": f"Discovered subdomains ({used_source}): {', '.join(sorted(subdomains))}",
        "recommendation": "Review exposed subdomains and ensure unused ones are removed."
    }
