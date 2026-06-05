from fastapi import FastAPI
from scanner.engine import ScannerEngine
from scanner.report import ReportBuilder

app = FastAPI()

@app.post("/scan")
def scan_target(target: dict):
    url = target.get("url")
    engine = ScannerEngine(url)
    results = engine.run()
    report = ReportBuilder(url, results)
    return {
        "summary": report.summary(),
        "results": results
    }
