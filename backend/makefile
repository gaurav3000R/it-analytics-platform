# Completing the Makefile with all targets

#===== ./backend/Makefile =====

.PHONY: install dev test clean docker-build docker-run setup-data train-models

# Installation
install:
	pip install -r requirements.txt

# Development
dev:
	python app/main.py --run-server

# Testing
test:
	pytest tests/ -v --cov=app

test-watch:
	pytest-watch tests/ -v

# Data setup
setup-data:
	python app/main.py --setup-data

train-models:
	python app/main.py --train-models

full-setup: install setup-data train-models

# Docker
docker-build:
	docker build -t it-analytics-backend .

docker-run:
	docker run -p 8000:8000 it-analytics-backend

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f it_analytics.db
	rm -f test.db
	rm -rf models/*.pkl

# Linting and formatting
lint:
	flake8 app/ tests/
	black --check app/ tests/

format:
	black app/ tests/
	isort app/ tests/

# Database
db-migrate:
	alembic upgrade head

db-reset:
	rm -f it_analytics.db
	python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# API Documentation
docs:
	python -c "import webbrowser; webbrowser.open('http://localhost:8000/docs')"