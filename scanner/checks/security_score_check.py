def run_check(target_url, all_results=None):
    name = "Security Score"

    # If the engine didn't pass results in, fail cleanly
    if all_results is None:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": "Security score requires aggregated results.",
            "recommendation": "Pass all check results into the scoring engine."
        }

    # Start at 100 and subtract penalties
    score = 100
    penalties = []

    for result in all_results:
        status = result.get("status", "pass")
        severity = result.get("severity", "low")
        check_name = result.get("name", "Unknown Check")

        if status == "warn":
            if severity == "low":
                score -= 3
            elif severity == "medium":
                score -= 7
            elif severity == "high":
                score -= 12
            penalties.append(f"{check_name}: warn/{severity}")

        elif status == "error":
            if severity == "low":
                score -= 5
            elif severity == "medium":
                score -= 10
            elif severity == "high":
                score -= 20
            penalties.append(f"{check_name}: error/{severity}")

    # Clamp score
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    # Letter grade
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

    # Map score to status + severity
    if score >= 80:
        status = "pass"
        severity = "low"
    elif score >= 60:
        status = "warn"
        severity = "medium"
    else:
        status = "error"
        severity = "high"

    # Build details
    details = f"Score: {score}/100, Grade: {grade}"
    if penalties:
        details += " | Penalties: " + ", ".join(penalties)

    return {
        "name": name,
        "status": status,
        "severity": severity,
        "details": details,
        "recommendation": (
            "Improve WARN and ERROR findings in other checks to raise your score."
        )
    }
