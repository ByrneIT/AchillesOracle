import socket
import ssl

def run_check(target_url):
    name = "TLS Version and Cipher Check"

    try:
        # Extract hostname and port
        hostname = (
            target_url.replace("https://", "")
                      .replace("http://", "")
                      .split("/")[0]
        )

        if ":" in hostname:
            host, port_str = hostname.split(":", 1)
            port = int(port_str)
        else:
            host = hostname
            port = 443

        context = ssl.create_default_context()
        # We want to see what the server negotiates by default
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                tls_version = ssock.version()          # e.g. 'TLSv1.2', 'TLSv1.3'
                cipher = ssock.cipher()                # (cipher_name, protocol, secret_bits)

        version = tls_version or "Unknown"
        cipher_name = cipher[0] if cipher else "Unknown"
        bits = cipher[2] if cipher else "Unknown"

        # Basic classification
        if version in ("TLSv1.2", "TLSv1.3"):
            status = "pass"
            severity = "low"
            recommendation = "TLS configuration is using a modern protocol version."
        elif version in ("TLSv1", "TLSv1.1"):
            status = "warn"
            severity = "medium"
            recommendation = (
                "Server negotiates outdated TLS versions (TLS 1.0/1.1). "
                "Disable them and enforce TLS 1.2+."
            )
        elif version is None or version == "Unknown":
            status = "error"
            severity = "high"
            recommendation = "Unable to determine TLS version. Check server configuration."
        else:
            # Anything older than TLSv1 is considered bad
            status = "fail"
            severity = "high"
            recommendation = (
                f"Server negotiates insecure protocol ({version}). "
                "Disable legacy SSL/TLS versions and enforce TLS 1.2+."
            )

        details = (
            f"Negotiated TLS version: {version}; "
            f"Cipher: {cipher_name} ({bits} bits)"
        )

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
            "recommendation": "TLS handshake failed. Verify that the server supports HTTPS and is reachable."
        }
