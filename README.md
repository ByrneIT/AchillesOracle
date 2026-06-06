# AchillesOracle

Local development and quick start

Prerequisites
- Python 3.10+ (recommended) and a virtual environment
- Node.js (for the UI) and npm

Backend (FastAPI)

1. Activate the virtualenv:

```powershell
# Windows (from project root)
env\Scripts\activate
```

2. Install Python deps:

```powershell
pip install -r requirements.txt
```

3. Start the backend server:

```powershell
env\Scripts\python.exe -m uvicorn api.server:app --reload --port 8000
```

Frontend (Vite + React)

1. Install node deps and start dev server:

```powershell
cd ui
npm install
npm run dev
```

2. Open http://localhost:5173/ in your browser.

End-to-end scan
- Use the UI input and click "Run Scan" to POST to `/scan` (proxied to backend in dev).

Notes
- During development the Vite dev server proxies `/scan` and `/report` to the backend (`127.0.0.1:8000`).
- If you see a blank page, ensure `ui/index.html` exists (Vite needs a processed index for the dev client).

