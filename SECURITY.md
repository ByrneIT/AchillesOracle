# Security analysis and hardening guidance

Overview
--------
This repository is a FastAPI-based scanner service. This document summarizes the current security posture, recommended mitigations, and quick commands to run automated checks.

Key findings & recommendations
-----------------------------
- Secrets: `SECRET_KEY` must not be committed. Use environment variables or Vault. See `achillesoracle/settings.py` for Vault integration.
- Dependencies: run `pip-audit` regularly and pin/update dependencies.
- Static analysis: run `bandit` on the codebase and triage findings.
- Transport: enforce HTTPS in front of the app (reverse proxy / load balancer). Disable TLS 1.0/1.1 and weak ciphers.
- Headers: add HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and appropriate CORS restrictions.
- Containers: run as non-root user, keep images minimal and scanned.

How to run the basic automated checks locally
--------------------------------------------
1. Install dev dependencies (recommended in a virtualenv):

```bash
python -m pip install --upgrade pip
if [ -f dev-requirements.txt ]; then pip install -r dev-requirements.txt; fi
pip install bandit pip-audit
```

2. Run tests and static checks:

```bash
pytest -q
bandit -r achillesoracle -lll
pip-audit
```

Deployment recommendations
--------------------------
- Use a reverse proxy (e.g. nginx) terminating TLS and forwarding to the app on a private network.
- Store secrets in a managed secrets store (HashiCorp Vault, AWS Secrets Manager) and avoid `.env` in production.
- Run regular dependency scanning in CI and block merges on critical findings.
- Use a Web Application Firewall (WAF) if exposed to the public internet.

Reporting and disclosures
------------------------
If you find a vulnerability, open an issue with the `security` label or follow the project's disclosure policy.
