import argparse
from scanner.engine import ScannerEngine
from scanner.report import ReportBuilder

def main():
    parser = argparse.ArgumentParser(description="Website Security Scanner")
    parser.add_argument("url", help="Target URL to scan")

    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--markdown", help="Output Markdown report to file")
    parser.add_argument("--html", help="Output HTML report to file")
    parser.add_argument("--output", help="Output file for JSON")

    args = parser.parse_args()

    engine = ScannerEngine(args.url)
    results = engine.run()

    report = ReportBuilder(args.url, results)

    # Default console summary
    print("\n=== SECURITY SCAN SUMMARY ===")
    print(report.summary())
    print(f"Score: {report.score}/100")
    print(f"Grade: {report.grade}")
    print("=============================\n")

    # JSON output to console
    if args.json and not args.output:
        print(report.to_json())

    # JSON output to file
    if args.output:
        with open(args.output, "w") as f:
            f.write(report.to_json())
        print(f"JSON report saved to {args.output}")

    # Markdown output
    if args.markdown:
        with open(args.markdown, "w") as f:
            f.write(report.to_markdown())
        print(f"Markdown report saved to {args.markdown}")

    # HTML output
    if args.html:
        with open(args.html, "w") as f:
            f.write(report.to_html())
        print(f"HTML report saved to {args.html}")

if __name__ == "__main__":
    main()
