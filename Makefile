.PHONY: help install lint test up down build clean migrate

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt

lint: ## Проверить код линтерами
	@echo "Running black..."
	black --check .
	@echo "Running isort..."
	isort --check-only .
	@echo "Running flake8..."
	flake8 .

lint-fix: ## Исправить форматирование кода
	black .
	isort .

test: ## Запустить тесты
	pytest tests/ -v

type-check: ## Проверить типы с mypy
	mypy app/

up: ## Запустить сервисы
	docker compose up -d --build

down: ## Остановить сервисы
	docker compose down

build: ## Собрать Docker образ
	docker compose build

logs: ## Показать логи
	docker compose logs -f

clean: ## Очистить Docker ресурсы
	docker compose down -v
	docker system prune -f

migrate: ## Выполнить миграции (placeholder)
	@echo "Migrations are handled automatically by SQLAlchemy"

check: lint test ## Запустить все проверки