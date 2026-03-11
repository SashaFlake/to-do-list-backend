.PHONY: help install dev run test docker-build docker-up docker-down helm-install helm-upgrade helm-uninstall

help:
	@echo "Available commands:"
	@echo "  install        Install dependencies"
	@echo "  dev            Run development server"
	@echo "  test           Run tests"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-up      Start Docker Compose"
	@echo "  docker-down    Stop Docker Compose"
	@echo "  helm-install   Install Helm chart"
	@echo "  helm-upgrade   Upgrade Helm chart"
	@echo "  helm-uninstall Uninstall Helm chart"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

docker-build:
	docker build -t fastapi-app:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

helm-install:
	helm install fastapi-app ./helm/fastapi-app --namespace fastapi-app --create-namespace

helm-upgrade:
	helm upgrade fastapi-app ./helm/fastapi-app --namespace fastapi-app

helm-uninstall:
	helm uninstall fastapi-app --namespace fastapi-app
