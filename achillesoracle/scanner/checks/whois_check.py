import re
from datetime import datetime
from achillesoracle.scanner.utils import safe_get, safe_resolve, make_result


def _parse_iso_date(date_str):
    try:
        if isinstance(date_str, str) and date_str.endswith("Z"):
            # make compatible with fromisoformat
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        pass

    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            pass
    return None


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

        rdap_url = f"https://rdap.org/domain/{domain}"

        resp = safe_get(rdap_url, timeout=8)
        if resp is None:
            return make_result(
                name,
                "soft-fail",
                "low",
                f"WHOIS/RDAP lookup failed or timed out for {domain}",
                "WHOIS lookup unavailable; treating as neutral (soft-fail).",
            )

        if resp.status_code != 200:
            return make_result(
                name,
                "soft-fail",
                "low",
                f"RDAP lookup returned status {resp.status_code}",
                "WHOIS lookup unavailable; treating as neutral (soft-fail).",
            )

        try:
            data = resp.json()
        except Exception:
            return make_result(
                name,
                "soft-fail",
                "low",
                "Unable to parse RDAP response",
                "WHOIS lookup unavailable; treating as neutral (soft-fail).",
            )

        created = None
        expires = None

        # Try to locate event dates in RDAP 'events'
        for ev in (data.get("events") or []):
            if not isinstance(ev, dict):
                continue
            action = (ev.get("eventAction") or ev.get("action") or "").lower()
            date_str = ev.get("eventDate") or ev.get(
                "event_date") or ev.get("date")
            if not date_str:
                continue
            parsed = _parse_iso_date(str(date_str))
            if not parsed:
                continue
            if "registration" in action or "create" in action:
                if not created:
                    created = parsed
            if "expiration" in action or "expire" in action:
                if not expires:
                    expires = parsed

        # Fallback: check for common top-level fields
        if not created:
            for k in ("registration", "created", "create_date", "registered"):
                if k in data and data.get(k):
                    parsed = _parse_iso_date(str(data.get(k)))
                    if parsed:
                        created = parsed
                        break

        if not expires:
            for k in ("expiration", "expires", "expiry", "expire_date"):
                if k in data and data.get(k):
                    parsed = _parse_iso_date(str(data.get(k)))
                    if parsed:
                        expires = parsed
                        break

        # If RDAP didn't provide useful WHOIS data, treat as soft-fail (neutral)
        if not created and not expires:
            return {
                "name": name,
                "status": "soft-fail",
                "severity": "low",
                "details": "RDAP returned no registration/expiration information",
                "recommendation": "WHOIS lookup returned insufficient data; treating as neutral (soft-fail)."
            }

        now = datetime.utcnow()
        age_days = (now - created).days if created else None
        days_to_expire = (expires - now).days if expires else None

        # DNSSEC check (best-effort) using safe resolver
        dnssec_status = "unknown"
        answers = safe_resolve(domain, "DNSKEY")
        if answers is None:
            dnssec_status = "unknown"
        elif isinstance(answers, list) and len(answers) == 0:
            dnssec_status = "disabled"
        else:
            dnssec_status = "enabled"

        details = (
            f"Created: {created}; "
            f"Expires: {expires}; "
            f"Domain age: {age_days} days; "
            f"DNSSEC: {dnssec_status}"
        )

        # Classification - only escalate when RDAP provided concrete info
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
        return make_result(
            name,
            "soft-fail",
            "low",
            f"WHOIS check encountered an unexpected error: {e}",
            "WHOIS check could not be completed; treated as neutral (soft-fail).",
        )
