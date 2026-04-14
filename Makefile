.PHONY: help install scrape-legacy analyze-hate generate-pdf clean

help:
	@echo "MTG Scraper - Available Commands"
	@echo "================================"
	@echo "make install        - Install dependencies using uv"
	@echo "make scrape-legacy  - Run Legacy format scraper and export to CSV"
	@echo "make analyze-hate   - Analyze hate cards from latest scrape"
	@echo "make generate-pdf   - Generate printable PDF from latest hate cards report"
	@echo "make clean          - Remove .venv and cache files"

install:
	uv sync

scrape-legacy:
	uv run python scripts/scrape_legacy.py $(ARGS)

analyze-hate:
	uv run python scripts/analyze_hate_cards.py

generate-pdf:
	uv run python scripts/generate_pdf_report.py

clean:
	rm -rf .venv __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
