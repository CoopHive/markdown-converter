.PHONY: uv-download
uv-download:
	curl -LsSf https://astral.sh/uv/install.sh | sh

.PHONY: install
install:
	rm -rf .venv && uv venv
	uv pip install .[dev]