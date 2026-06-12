from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.models import ScanRequest
from api.adapters import run_scan
from api.billing import router as billing_router
from achillesoracle.settings import settings

_is_prod = settings.APP_ENV.lower() == "production"

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AchillesOracle",
    version="0.1.0",
    # Swagger/ReDoc disabled in production — enable locally by setting APP_ENV=development
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# TODO: restrict allow_origins to your domain(s) before going fully public
#   e.g. allow_origins=["https://achillesoracle.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(billing_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": "0.1.0"}


@app.post("/scan")
@limiter.limit("20/minute")
def scan(request: Request, body: ScanRequest):
    return run_scan(str(body.url))


@app.get("/report/md", response_class=PlainTextResponse)
@limiter.limit("20/minute")
def get_markdown_report(request: Request, url: str):
    try:
        validated = ScanRequest(url=url)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    result = run_scan(str(validated.url))
    return result["report_md"]


@app.get("/report/html", response_class=HTMLResponse)
@limiter.limit("20/minute")
def get_html_report(request: Request, url: str):
    try:
        validated = ScanRequest(url=url)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    result = run_scan(str(validated.url))
    return result["report_html"]
