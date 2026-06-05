import requests

def run_check(target_url):
    name = "X-Frame-Options / Frame-Ancestors Check"

    try:
        response = requests.get(target_url, timeout=6)
        headers = response.headers

        xfo = headers.get("X-Frame-Options")
        csp = headers.get("Content-Security-Policy")

        issues = []
        details = []

        # --- X-Frame-Options ---
        if xfo:
            xfo_lower = xfo.lower().strip()
            details.append(f"X-Frame-Options: {xfo}")

            if xfo_lower not in ["deny", "sameorigin"]:
                issues.append(f"X-Frame-Options uses deprecated or unsafe value: {xfo}")
        else:
            issues.append("Missing X-Frame-Options header.")

        # --- CSP frame-ancestors ---
        fa = None
        if csp:
            csp_lower = csp.lower()
            if "frame-ancestors" in csp_lower:
                fa = csp_lower.split("frame-ancestors", 1)[1].split(";")[0].strip()
                details.append(f"frame-ancestors: {fa}")

                if fa == "*":
                    issues.append("frame-ancestors allows all origins (*).")
                elif fa.startswith("http://"):
                    issues.append("frame-ancestors allows insecure (HTTP) origins.")
        else:
            details.append("No CSP header present.")

        # --- Conflict detection ---
        if xfo and fa:
            if "deny" in xfo_lower and fa != "'none'":
                issues.append("Conflict: X-Frame-Options=DENY but frame-ancestors is not 'none'.")

        # --- Result logic ---
        if issues:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": " | ".join(details) + " | Issues: " + ", ".join(issues),
                "recommendation": (
                    "Use either X-Frame-Options: DENY or SAMEORIGIN, or set "
                    "Content-Security-Policy: frame-ancestors 'none' or 'self'. "
                    "Avoid deprecated or conflicting configurations."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": " | ".join(details),
            "recommendation": "Clickjacking protections appear correctly configured."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to evaluate X-Frame-Options / frame-ancestors."
        }
