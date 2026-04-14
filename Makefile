.PHONY: help install scrape-legacy analyze-hate generate-pdf clean clean-output

help:
	@echo "MTG Scraper - Available Commands"
	@echo "================================"
	@echo "make install        - Install dependencies using uv"
	@echo "make scrape-legacy  - Run Legacy format scraper and export to CSV"
	@echo "make analyze-hate   - Analyze hate cards from latest scrape"
	@echo "make generate-pdf   - Generate printable PDF from latest hate cards report"
	@echo "make clean-output   - Remove _output directory"
	@echo "make clean          - Remove .venv and cache files"

install:
	uv sync

scrape-legacy:
	uv run python scripts/scrape_legacy.py $(ARGS)

analyze-hate:
	uv run python scripts/analyze_hate_cards.py

generate-pdf:
	uv run python scripts/generate_pdf_report.py

clean-output:
	@if [ ! -f "pyproject.toml" ]; then echo "Error: pyproject.toml not found. Run from project root."; exit 1; fi
	@if [ ! -d "mtgscrap" ]; then echo "Error: mtgscrap module directory not found. Wrong repo."; exit 1; fi
	@if ! git remote -v | grep -q "mtgscrap"; then echo "Error: Not in mtgscrap repository. Remote URL doesn't match."; exit 1; fi
	@if [ -z "$$(git branch --show-current | grep -E '^master$$')" ] && [ -z "$$(git branch --show-current | grep -E '^main$$')" ]; then echo "Error: Not on master/main branch. Refusing to delete _output."; exit 1; fi
	rm -rf _output

clean:
	rm -rf .venv __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
