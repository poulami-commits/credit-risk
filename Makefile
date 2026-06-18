.PHONY: install train evaluate test run docker-build docker-run clean

install:
	pip install -r requirements.txt

train:
	python scripts/train_pipeline.py

evaluate:
	python scripts/evaluate.py

test:
	pytest tests/ -v --tb=short

run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t credit-risk-engine:latest .

docker-run:
	docker-compose up --build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	rm -f models/*.joblib models/*.pkl; \
	echo "Clean complete."
