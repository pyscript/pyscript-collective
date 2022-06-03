tag := latest
git_hash ?= $(shell git log -1 --pretty=format:%h)

base_dir ?= $(shell git rev-parse --show-toplevel)
src_dir ?= $(base_dir)/src
examples ?=  ../$(base_dir)/examples
app_dir ?= $(shell git rev-parse --show-prefix)

CONDA_EXE := conda
CONDA_ENV ?= ./env
env := $(CONDA_ENV)
conda_run := $(CONDA_EXE) run -p $(env)

test:
	$(conda_run) pytest -vv $(ARGS) tests/ --log-cli-level=warning

fmt: fmt-py fmt-ts
	@echo "Format completed"

fmt-check: fmt-ts-check fmt-py-check
	@echo "Format check completed"

fmt-ts:
	npm run format

fmt-ts-check:
	npm run format:check

fmt-py:
	$(conda_run) black --skip-string-normalization .
	$(conda_run) isort --profile black .

fmt-py-check:
	$(conda_run) black -l 88 --check .

lint: lint-ts
	@echo "Format check completed"

lint-ts:
	$(conda_run) npm run lint

.PHONY: $(MAKECMDGOALS)
