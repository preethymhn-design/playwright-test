## Makefile for ragas-simple
## Run `make help` to see all commands.

PYTHON := python

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[33m%-22s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install -r requirements.txt

test: ## Run all tests (no API key needed)
	$(PYTHON) -m pytest tests/ -v

test-fast: ## Run tests without pytest
	$(PYTHON) tests/test_sample_and_dataset.py
	$(PYTHON) tests/test_metrics_logic.py

example: ## Run the basic example (needs GEMINI_API_KEY or other provider key)
	$(PYTHON) examples/basic_rag_eval.py

clean: ## Remove generated files
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -f eval_results.csv sample_data.jsonl

.PHONY: help install test test-fast example clean
