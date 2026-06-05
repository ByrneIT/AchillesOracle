import socket

def run_check(target_url):
    name = "Open Ports Check"

    hostname = target_url.replace("https://", "").replace("http://", "").split("/")[0]

    common_ports = {
        80: "HTTP",
        443: "HTTPS",
        21: "FTP",
        22: "SSH",
        25: "SMTP",
        3306: "MySQL",
        8080: "HTTP-Alt"
    }

    open_ports = []

    for port, service in common_ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((hostname, port))
            sock.close()

            if result == 0:
                open_ports.append(f"{port} ({service})")

        except Exception:
            pass

    if open_ports:
        return {
            "name": name,
            "status": "warn",
            "severity": "medium",
            "details": f"Open ports detected: {', '.join(open_ports)}",
            "recommendation": "Verify that these services should be publicly accessible."
        }

    return {
        "name": name,
        "status": "pass",
        "severity": "low",
        "details": "No common ports appear to be open.",
        "recommendation": "No action needed."
    }
