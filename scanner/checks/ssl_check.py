import ssl
import socket
from datetime import datetime

def run_check(target_url):
    name = "SSL Certificate Check"

    try:
        hostname = target_url.replace("https://", "").replace("http://", "").split("/")[0]

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        # Extract expiration date
        expires = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
        days_left = (expires - datetime.utcnow()).days

        if days_left < 0:
            return {
                "name": name,
                "status": "fail",
                "severity": "high",
                "details": f"Certificate expired {abs(days_left)} days ago.",
                "recommendation": "Renew the SSL certificate immediately."
            }

        elif days_left < 30:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": f"Certificate expires in {days_left} days.",
                "recommendation": "Renew the certificate soon to avoid downtime."
            }

        else:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": f"Certificate is valid. {days_left} days remaining.",
                "recommendation": "No action needed."
            }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to verify SSL certificate."
        }
