.PHONY: build backend frontend up down test package

build: backend frontend

backend:
	docker build -t achillesoracle-backend -f Dockerfile .

frontend:
	docker build -t achillesoracle-frontend -f ui/Dockerfile .

up:
	docker-compose up -d --build

down:
	docker-compose down

test:
	pytest -q

package:
	python -m build


sec-scan:
	python -m pip install --upgrade pip
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
	if [ -f dev-requirements.txt ]; then pip install -r dev-requirements.txt; fi
	pip install bandit pip-audit || true
	pytest -q || true
	bandit -r achillesoracle -lll || true
	pip-audit || true

pentest:
	@echo "Run manual pentest steps; see PENTEST.md for checklist"
	@echo "Examples: nmap -Pn -sV -p- <target> ; docker run --rm owasp/zap2docker-stable zap-baseline.py -t <target> -r zap-report.html"
