tag := latest
git_hash ?= $(shell git log -1 --pretty=format:%h)

CONDA_EXE := conda
CONDA_ENV ?= ./env
env := $(CONDA_ENV)
conda_run := $(CONDA_EXE) run -p $(env)

setup:
	$(CONDA_EXE) env $(shell [ -d $(env) ] && echo update || echo create) -p $(env) --file environment.yml
	$(conda_run) playwright install
	$(CONDA_EXE) install -c anaconda pytest
# 	pip install playwright

clean:
	find . -name \*.py[cod] -delete
	rm -rf .pytest_cache .coverage coverage.xml

clean-all: clean
	rm -rf $(env) *.egg-info

shell:
	@export CONDA_ENV_PROMPT='<{name}>'
	@echo 'conda activate $(env)'

test:
	$(conda_run) pytest -vv $(ARGS) tests/ --log-cli-level=warning

test-py:
	@echo "Tests are coming :( this is a placeholder and it's meant to fail!"
	$(conda_run) pytest -vv $(ARGS) tests/ --log-cli-level=warning

test-ts:
	@echo "Tests are coming :( this is a placeholder and it's meant to fail!"
	npm run tests

fmt: fmt-py fmt-ts
	@echo "Format completed"

fmt-check: fmt-ts-check fmt-py-check
	@echo "Format check completed"

fmt-py:
	$(conda_run) black --skip-string-normalization .
	$(conda_run) isort --profile black .

fmt-py-check:
	$(conda_run) black -l 88 --check .

lint: lint-ts
	@echo "Format check completed"

.PHONY: $(MAKECMDGOALS)
