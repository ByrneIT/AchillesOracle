from pydantic import BaseModel, HttpUrl, field_validator


class ScanRequest(BaseModel):
    url: HttpUrl

    @field_validator('url')
    @classmethod
    def no_private_ranges(cls, v):
        import ipaddress
        import socket
        from urllib.parse import urlparse

        host = urlparse(str(v)).hostname
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(host))
            if ip.is_private or ip.is_loopback:
                raise ValueError(
                    "Scanning private/internal addresses not permitted")
        except socket.gaierror:
            pass  # let DNS failures surface in the scanner
        return v
