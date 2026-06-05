import json

class ReportBuilder:
    def __init__(self, url, results):
        self.url = url
        self.results = results
        self.score = self._extract_score()
        self.grade = self._extract_grade()

    def _extract_score(self):
        for r in self.results:
            if r.get("name") == "Security Score":
                details = r.get("details", "")
                if "Score:" in details:
                    try:
                        return int(details.split("Score:")[1].split("/")[0].strip())
                    except:
                        return 0
        return 0

    def _extract_grade(self):
        for r in self.results:
            if r.get("name") == "Security Score":
                details = r.get("details", "")
                if "Grade:" in details:
                    try:
                        return details.split("Grade:")[1].split()[0].strip()
                    except:
                        return "F"
        return "F"

    def summary(self):
        passed = sum(1 for r in self.results if r.get("status") == "pass")
        warnings = sum(1 for r in self.results if r.get("status") == "warn")
        errors = sum(1 for r in self.results if r.get("status") == "error")

        return (
            f"Checks Passed: {passed}, "
            f"Warnings: {warnings}, "
            f"Errors: {errors}"
        )

    def to_json(self):
        return json.dumps({
            "url": self.url,
            "score": self.score,
            "grade": self.grade,
            "summary": self.summary(),
            "results": self.results
        }, indent=4)

    def to_markdown(self):
        md = []
        md.append(f"# Security Scan Report for {self.url}\n")
        md.append(f"**Score:** {self.score}/100")
        md.append(f"**Grade:** {self.grade}\n")

        md.append("## Summary\n")
        md.append(self.summary() + "\n")

        md.append("## Findings\n")
        for result in self.results:
            name = result.get("name", "Unknown Check")
            status = result.get("status", "unknown")
            severity = result.get("severity", "unknown")
            details = result.get("details", "")
            recommendation = result.get("recommendation", "")

            md.append(f"### {name}")
            md.append(f"- **Status:** {status}")
            md.append(f"- **Severity:** {severity}")
            md.append(f"- **Details:** {details}")
            md.append(f"- **Recommendation:** {recommendation}\n")

        return "\n".join(md)

    def to_html(self):
        html = []
        html.append("<html><head><title>Security Scan Report</title></head><body>")
        html.append(f"<h1>Security Scan Report for {self.url}</h1>")
        html.append(f"<p><strong>Score:</strong> {self.score}/100</p>")
        html.append(f"<p><strong>Grade:</strong> {self.grade}</p>")

        html.append("<h2>Summary</h2>")
        html.append(f"<p>{self.summary()}</p>")

        html.append("<h2>Findings</h2>")
        for result in self.results:
            name = result.get("name", "Unknown Check")
            status = result.get("status", "unknown")
            severity = result.get("severity", "unknown")
            details = result.get("details", "")
            recommendation = result.get("recommendation", "")

            html.append("<div style='margin-bottom:20px;'>")
            html.append(f"<h3>{name}</h3>")
            html.append(f"<p><strong>Status:</strong> {status}</p>")
            html.append(f"<p><strong>Severity:</strong> {severity}</p>")
            html.append(f"<p><strong>Details:</strong> {details}</p>")
            html.append(f"<p><strong>Recommendation:</strong> {recommendation}</p>")
            html.append("</div>")

        html.append("</body></html>")
        return "\n".join(html)
