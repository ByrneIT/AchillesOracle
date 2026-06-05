def make_result(name, status, severity, details, recommendation):
    return {
        "name": name,
        "status": status,
        "severity": severity,
        "details": details,
        "recommendation": recommendation
    }

