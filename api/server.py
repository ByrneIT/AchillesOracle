from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, HTMLResponse
from api.models import ScanRequest
from api.adapters import run_scan

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": "0.1.0"}


@app.post("/scan")
def scan(request: ScanRequest):
    return run_scan(request.url)


@app.get("/report/md", response_class=PlainTextResponse)
def get_markdown_report(url: str):
    result = run_scan(url)
    return result["report_md"]


@app.get("/report/html", response_class=HTMLResponse)
def get_html_report(url: str):
    result = run_scan(url)
    return result["report_html"]
