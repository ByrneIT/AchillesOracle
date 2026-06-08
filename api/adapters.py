from achillesoracle.scanner.engine import ScannerEngine
from achillesoracle.scanner.report import ReportBuilder


def run_scan(url: str):
    try:
        engine = ScannerEngine(url)
        results = engine.run()

        # Build a rich report object from the list of check results
        report = ReportBuilder(url, results)

        passed = sum(1 for r in results if r.get("status") == "pass")
        warnings = sum(1 for r in results if r.get("status") == "warn")
        errors = sum(1 for r in results if r.get("status") == "error")
        issues = [r for r in results if r.get("status") in ("warn", "error")]

        return {
            "url": url,
            "score": report.score,
            "grade": report.grade,
            "passed": passed,
            "warnings": warnings,
            "errors": errors,
            "issues": issues,
            "report_md": report.to_markdown(),
            "report_html": report.to_html(),
            "results": results,
        }
    except Exception as e:
        # Global adapter fallback to ensure API surface stays stable
        fallback = [{
            "name": "Scan Engine",
            "status": "soft-fail",
            "severity": "low",
            "details": f"Scan failed: {e}",
            "recommendation": "Scan encountered an unexpected error and was treated as neutral."
        }]

        report_md = f"# Security Scan Report for {url}\n\nScan could not be completed."
        report_html = f"<html><body><h1>Security Scan Report for {url}</h1><p>Scan could not be completed.</p></body></html>"

        return {
            "url": url,
            "score": 0,
            "grade": "F",
            "passed": 0,
            "warnings": 0,
            "errors": 1,
            "issues": fallback,
            "report_md": report_md,
            "report_html": report_html,
            "results": fallback,
        }
