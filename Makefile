PYTHON=python
PIP=pip
VENV=.venv

.PHONY: setup fmt lint test run-sample ui precommit-install

setup:
	@if not exist $(VENV) ( $(PYTHON) -m venv $(VENV) )
	@"$(VENV)\\Scripts\\pip" install -U pip
	@"$(VENV)\\Scripts\\pip" install -r requirements.txt
	@"$(VENV)\\Scripts\\python" tools/bootstrap_assets.py

fmt:
	@"$(VENV)\\Scripts\\python" -m black .

lint:
	@"$(VENV)\\Scripts\\python" -m ruff check .
	@"$(VENV)\\Scripts\\python" -m black --check .

test:
	@"$(VENV)\\Scripts\\python" -m pytest -q

run-sample:
	@"$(VENV)\\Scripts\\python" -m app.main generate --brief briefs/sample_brief.json --out outputs --provider mock --ratios 1:1,9:16,16:9 --locales en-US,es-MX --max-variants 2 --log-json

ui:
	@"$(VENV)\\Scripts\\streamlit" run app/ui.py

precommit-install:
	@"$(VENV)\\Scripts\\pre-commit" install


