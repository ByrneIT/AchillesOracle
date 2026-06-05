import re
import requests
from bs4 import BeautifulSoup

# Known libraries and regex patterns to extract versions
LIB_PATTERNS = {
    "jquery": r"jquery[-.]?(\d+\.\d+\.\d+)",
    "bootstrap": r"bootstrap[-.]?(\d+\.\d+\.\d+)",
    "react": r"react[-.]?(\d+\.\d+\.\d+)",
    "angular": r"angular[-.]?(\d+\.\d+\.\d+)",
    "vue": r"vue[-.]?(\d+\.\d+\.\d+)",
    "lodash": r"lodash[-.]?(\d+\.\d+\.\d+)",
    "moment": r"moment[-.]?(\d+\.\d+\.\d+)",
}

def run_check(target_url):
    name = "JavaScript Library Version Detection"

    try:
        response = requests.get(target_url, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")

        scripts = [s.get("src") for s in soup.find_all("script") if s.get("src")]
        results = []
        issues = []

        for src in scripts:
            for lib, pattern in LIB_PATTERNS.items():
                match = re.search(pattern, src, re.IGNORECASE)
                if match:
                    version = match.group(1)
                    results.append(f"{lib}: {version}")

                    # Flag old versions (simple heuristic)
                    major = int(version.split(".")[0])
                    if major < 2 and lib == "jquery":
                        issues.append(f"{lib} {version} is outdated and vulnerable.")
                    if major < 4 and lib == "bootstrap":
                        issues.append(f"{lib} {version} is outdated.")
                    if major < 17 and lib == "react":
                        issues.append(f"{lib} {version} is outdated.")
                    if major < 3 and lib == "vue":
                        issues.append(f"{lib} {version} is outdated.")

        if not results:
            return {
                "name": name,
                "status": "pass",
                "severity": "low",
                "details": "No detectable JavaScript libraries found.",
                "recommendation": "No action needed."
            }

        details = " | ".join(results)

        if issues:
            return {
                "name": name,
                "status": "warn",
                "severity": "medium",
                "details": details + " | Issues: " + ", ".join(issues),
                "recommendation": (
                    "Update outdated JavaScript libraries to reduce security risks. "
                    "Consider using CDN integrity attributes (SRI) for added protection."
                )
            }

        return {
            "name": name,
            "status": "pass",
            "severity": "low",
            "details": details,
            "recommendation": "JavaScript libraries appear up to date."
        }

    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "severity": "high",
            "details": str(e),
            "recommendation": "Unable to analyze JavaScript libraries."
        }
