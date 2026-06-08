def run_check(target_url, all_results=None):
    """Aggregate individual check results into a normalized security score.

    Returns a dictionary with numeric score (0-100), letter grade, and
    an overall status/severity. The implementation:
    - weights severity properly (critical>high>medium>low)
    - gives positive credit for passes
    - normalizes across the number and weight of checks
    - caps per-check influence by using a weighted average (one check cannot
      single-handedly tank the whole score)
    - applies category weighting (security > performance > seo)
    - applies minimum score floors based on the worst failing severity
    - handles malformed entries gracefully and reports warnings
    """

    name = "Security Score"

    # Basic input validation
    if all_results is None:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": "Security score requires aggregated results.",
            "recommendation": "Pass a list of check result dictionaries into the scoring engine."
        }

    # Helper mappings
    status_fraction = {
        "pass": 1.0,
        "info": 0.95,
        "warn": 0.75,
        "error": 0.0,
        "skip": 1.0,
        # Soft-fail/neutral statuses should not reduce score
        "soft-fail": 1.0,
        "neutral": 1.0,
    }

    # Severity increases the importance of the check when averaging.
    # Keep these moderate so a single check cannot dominate the average.
    severity_weight = {
        "low": 1.0,
        "medium": 1.8,
        "high": 2.8,
        "critical": 5.0,
    }

    # Category weighting: security matters more than performance and SEO.
    category_weight = {
        "security": 1.5,
        "performance": 1.0,
        "seo": 0.9,
    }

    def infer_category_from_name(n):
        n = (n or "").lower()
        if any(k in n for k in ("ssl", "tls", "hsts", "csp", "x-frame", "x-content", "server", "whois", "ssrf", "permissions", "headers", "cookie", "security", "tls", "tls_check")):
            return "security"
        if any(k in n for k in ("speed", "performance", "cache", "cdn", "compress", "gzip", "minify")):
            return "performance"
        if any(k in n for k in ("sitemap", "robots", "seo", "index", "meta")):
            return "seo"
        return "security"

    # Normalize and sanitize input entries
    results = []
    warnings = []
    for idx, entry in enumerate(all_results or []):
        if not isinstance(entry, dict):
            warnings.append(
                f"Result #{idx + 1} is not a dict and was ignored.")
            continue

        name_field = entry.get("name") or entry.get("check") or "Unnamed Check"
        raw_status = entry.get("status", "pass")
        raw_sev = entry.get("severity", "low")
        raw_cat = entry.get("category")

        status = (raw_status or "").lower()
        severity = (raw_sev or "").lower()
        category = (raw_cat or "").lower() if raw_cat else None

        if status not in status_fraction:
            warnings.append(
                f"{name_field}: unknown status '{raw_status}', treating as 'warn'.")
            status = "warn"

        if severity not in severity_weight:
            warnings.append(
                f"{name_field}: unknown severity '{raw_sev}', treating as 'low'.")
            severity = "low"

        if not category:
            category = infer_category_from_name(name_field)

        if category not in category_weight:
            # Unknown categories are treated as neutral (performance-level)
            category = "performance"

        results.append({
            "name": name_field,
            "status": status,
            "severity": severity,
            "category": category,
        })

    if not results:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": "No valid check results available to score.",
            "recommendation": "Provide check result dictionaries with at least 'name', 'status', and 'severity'."
        }

    # Build per-category weighted aggregates so we can cap per-category penalties
    per_category_num = {}
    per_category_den = {}
    counts = {"pass": 0, "warn": 0, "error": 0}
    severity_counts = {k: 0 for k in severity_weight.keys()}
    per_check_summary = []

    for r in results:
        w_sev = severity_weight.get(r["severity"], 1.0)
        w_cat = category_weight.get(r["category"], 1.0)
        weight = w_sev * w_cat

        # Reduce impact of external-dependency checks (WHOIS, subdomain enumeration)
        name_l = (r.get("name") or "").lower()
        if "whois" in name_l or "subdomain" in name_l:
            weight *= 0.5

        frac = status_fraction.get(r["status"], 0.5)

        per_category_num[r["category"]] = per_category_num.get(
            r["category"], 0.0) + (weight * frac)
        per_category_den[r["category"]] = per_category_den.get(
            r["category"], 0.0) + weight

        counts[r["status"]] = counts.get(r["status"], 0) + 1
        severity_counts[r["severity"]] = severity_counts.get(
            r["severity"], 0) + 1
        per_check_summary.append(
            f"{r['name']}: {r['status']}/{r['severity']} (cat={r['category']})")

    # Apply per-category minimum fraction caps to avoid single-category domination
    # Caps only apply when a category contains multiple checks (so single-critical checks still behave)
    category_min_fraction = {
        "security": 0.5,
        "performance": 0.5,
        "seo": 0.6,
    }

    adjusted_num = 0.0
    adjusted_den = 0.0
    for cat, den in per_category_den.items():
        num = per_category_num.get(cat, 0.0)
        if den <= 0:
            continue
        cat_frac = num / den

        # Determine number of checks in this category
        cat_count = sum(1 for r in results if r["category"] == cat)
        if cat_count > 1:
            min_frac = category_min_fraction.get(cat, 0.5)
            if cat_frac < min_frac:
                cat_frac = min_frac

        adjusted_num += cat_frac * den
        adjusted_den += den

    weighted_avg = (adjusted_num / adjusted_den) if adjusted_den > 0 else 0.0
    raw_score = max(0, min(100, int(round(weighted_avg * 100))))

    # Minimum score floors based on worst failing severity.
    # If there are no failing checks, give a generous floor; if criticals exist, allow low scores.
    worst_rank = 0
    rank_map = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    failing_sevs = [r["severity"] for r in results if r["status"] != "pass"]
    if failing_sevs:
        # determine the worst (highest rank) severity among failures
        worst_sev = max(failing_sevs, key=lambda s: rank_map.get(s, 0))
        worst_rank = rank_map.get(worst_sev, 0)
    else:
        worst_rank = 0

    floor_map = {0: 90, 1: 75, 2: 70, 3: 60, 4: 0}
    floor = floor_map.get(worst_rank, 0)
    score = max(raw_score, floor)

    # Letter grade mapping (realistic thresholds)
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    # Overall status + severity derived from numeric score
    if score >= 80:
        overall_status = "pass"
        overall_severity = "low"
    elif score >= 60:
        overall_status = "warn"
        overall_severity = "medium"
    else:
        overall_status = "error"
        overall_severity = "high"

    details_parts = [f"Score: {score}/100", f"Grade: {grade}"]
    details_parts.append(
        f"Checks: {len(results)} (pass={counts.get('pass', 0)} warn={counts.get('warn', 0)} error={counts.get('error', 0)})")
    if warnings:
        details_parts.append("Warnings: " + " | ".join(warnings))

    return {
        "name": name,
        "status": overall_status,
        "severity": overall_severity,
        "score": score,
        "grade": grade,
        "details": " -- ".join(details_parts),
        "breakdown": per_check_summary,
        "recommendation": (
            "Address ERROR/WARN findings in high/critical severity checks first; re-run to recompute score."
        ),
    }
