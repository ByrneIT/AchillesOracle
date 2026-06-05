import requests

def run_check(target_url):
    name = "Technology Fingerprinting"

    try:
        response = requests.get(target_url, timeout=6)
        html = response.text.lower()
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}

        detected = []

        # --- SERVER TECHNOLOGIES ---
        server = headers.get("server", "")
        if server:
            detected.append(f"Server: {server}")

        # --- CDN / REVERSE PROXY ---
        if "cloudflare" in server or "cf-ray" in headers:
            detected.append("CDN: Cloudflare")
        if "akamai" in server:
            detected.append("CDN: Akamai")
        if "fastly" in server:
            detected.append("CDN: Fastly")
        if "sucuri" in server:
            detected.append("WAF: Sucuri")
        if "imperva" in server:
            detected.append("WAF: Imperva")
        if "cloudfront" in headers.get("via", ""):
            detected.append("CDN: AWS CloudFront")

        # --- PROGRAMMING LANGUAGES ---
        if "php" in server or "x-powered-by" in headers and "php" in headers.get("x-powered-by", ""):
            detected.append("Language: PHP")
        if "python" in html or "wsgi" in server:
            detected.append("Language: Python")
        if "node" in server or "express" in headers.get("x-powered-by", ""):
            detected.append("Language: Node.js")
        if "ruby" in server or "rails" in html:
            detected.append("Language: Ruby")
        if "asp.net" in server:
            detected.append("Language: ASP.NET")
        if "java" in server or "jsp" in html:
            detected.append("Language: Java")

        # --- FRAMEWORKS ---
        if "laravel" in html:
            detected.append("Framework: Laravel")
        if "django" in html:
            detected.append("Framework: Django")
        if "express" in headers.get("x-powered-by", ""):
            detected.append("Framework: Express.js")
        if "rails" in html:
            detected.append("Framework: Ruby on Rails")
        if "spring" in html:
            detected.append("Framework: Spring")
        if "flask" in html:
            detected.append("Framework: Flask")

        # --- HOSTING PROVIDERS (lightweight heuristics) ---
        if "cloudflare" in server:
            detected.append("Hosting: Cloudflare Pages / Cloudflare Network")
        if "amazon" in server or "cloudfront" in headers.get("via", ""):
            detected.append("Hosting: AWS")
        if "azure" in server:
            detected.append("Hosting: Azure")
        if "google" in server:
            detected.append("Hosting: Google Cloud")
        if "vercel" in html:
            detected.append("Hosting: Vercel")
        if "netlify" in html:
            detected.append("Hosting: Netlify")

        # --- RESULT LOGIC ---
        if not detected:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "No identifiable technologies detected.",
                "recommendation": "No action needed."
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": ", ".join(detected),
            "recommendation": "Review detected technologies and ensure they are up to date."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to perform technology fingerprinting."
        }
