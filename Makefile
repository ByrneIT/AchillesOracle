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
