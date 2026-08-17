.PHONY: install test eval lint dev

install:
	python3.11 -m pip install -e "api[dev]"

test:
	python3.11 -m pytest -c api/pyproject.toml -v --tb=short

eval:
	@if [ -f evals/run_eval.py ]; then \
		python3.11 evals/run_eval.py --offline --fail-under-f1 0.95 --max-weight-mae 1.0; \
	else \
		echo "evals/ not present yet — skipping"; \
	fi

lint:
	ruff check api tests scripts
	@if [ -d evals ]; then ruff check evals; fi
	@if [ -f web/package.json ]; then \
		cd web && npx tsc --noEmit && npm run lint; \
	fi

dev:
	uvicorn px.main:app --reload --app-dir api/src
