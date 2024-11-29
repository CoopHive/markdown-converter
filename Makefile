.PHONY: uv-download
uv-download:
	curl -LsSf https://astral.sh/uv/install.sh | sh

.PHONY: install
install:
	rm -rf .venv && uv venv
	. .venv/bin/activate && \
	uv pip install .

.PHONY: test
test:
	uv run pytest -c pyproject.toml tests/