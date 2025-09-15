.PHONY: help install install-dev test test-unit test-integration test-coverage lint format clean run run-docker js-install js-test js-test-unit js-test-integration js-test-coverage js-test-watch js-lint js-lint-fix js-run

# Default target
help:
	@echo "AgroTech AI - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Testing (Python):"
	@echo "  py-test         Run all Python tests (unit + integration)"
	@echo "  py-test-unit    Run Python unit tests only"
	@echo "  py-test-integration  Run Python integration tests only"
	@echo "  py-test-coverage     Run Python tests with coverage report"
	@echo ""
	@echo "Testing (JavaScript):"
	@echo "  js-test         Run all JavaScript tests (unit + integration)"
	@echo "  js-test-unit    Run JavaScript unit tests only"
	@echo "  js-test-integration  Run JavaScript integration tests only"
	@echo "  js-test-coverage     Run JavaScript tests with coverage report"
	@echo "  js-test-watch   Run JavaScript tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  py-lint         Run Python linting checks"
	@echo "  py-format       Format Python code with black and isort"
	@echo "  js-lint         Run JavaScript linting checks"
	@echo "  js-lint-fix     Run JavaScript linting with auto-fix"
	@echo ""
	@echo "Development:"
	@echo "  py-run       Start Python development server"
	@echo "  js-run       Start JavaScript development server"
	@echo "  run-docker   Start services with Docker Compose"
	@echo "  stop-docker  Stop Docker Compose services"
	@echo "  logs         View Docker Compose logs"
	@echo "  clean        Clean up generated files"

# Installation
install:
	cd server && pip install -e .

install-dev:
	cd server && pip install -e ".[dev,test]"

js-install:
	cd client && npm install

# Testing
py-test:
	cd server && python tests/test_runner.py all

py-test-unit:
	cd server && python tests/test_runner.py unit

py-test-integration:
	cd server && python tests/test_runner.py integration

py-test-coverage:
	cd server && python tests/test_runner.py coverage

py-test-ollama:
	cd server && python tests/test_runner.py ollama

# JavaScript Testing
js-test:
	cd client && npm test -- --run

js-test-unit:
	cd client && npm test tests/unit -- --run

js-test-integration:
	cd client && npm test tests/integration -- --run

js-test-coverage:
	cd client && npm run test:coverage

js-test-watch:
	cd client && npm run test:watch

# Code quality
py-lint:
	cd server && python tests/test_runner.py lint

py-format:
	cd server && python tests/test_runner.py format

js-lint:
	cd client && npm run lint

js-lint-fix:
	cd client && npm run lint:fix

# Development
py-run:
	cd server && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

js-run:
	cd client && npm run dev

run-docker:
	docker compose up --build

run-docker-detached:
	docker compose up --build -d

stop-docker:
	docker compose down

logs:
	docker compose logs -f

logs-server:
	docker compose logs -f api-server

logs-ollama:
	docker compose logs -f ollama

# Docker management
docker-rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up

docker-clean:
	docker compose down -v

# Cleanup
clean:
	# Python cleanup
	find server -type d -name "__pycache__" -exec rm -rf {} +
	find server -type f -name "*.pyc" -delete
	find server -type f -name "*.pyo" -delete
	find server -type f -name "*.pyd" -delete
	find server -type f -name ".coverage" -delete
	find server -type d -name "*.egg-info" -exec rm -rf {} +
	find server -type d -name ".pytest_cache" -exec rm -rf {} +
	find server -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf server/htmlcov/
	rm -rf server/coverage.xml
	rm -rf server/dist/
	rm -rf server/build/
	# JavaScript cleanup
	rm -rf client/dist/
	rm -rf client/coverage/
	rm -rf client/node_modules/.cache/
