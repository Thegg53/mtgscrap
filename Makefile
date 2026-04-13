.PHONY: help venv install install-dev scrape-legacy analyze-hate generate-pdf clean

help:
	@echo "MTG Scraper - Available Commands"
	@echo "================================"
	@echo "make venv           - Create Python 3.12+ virtual environment"
	@echo "make install        - Install dependencies (requires active venv)"
	@echo "make install-dev    - Install dependencies + dev tools"
	@echo "make scrape-legacy  - Run Legacy format scraper and export to CSV"
	@echo "make analyze-hate   - Analyze hate cards from latest scrape"
	@echo "make generate-pdf   - Generate printable PDF from latest hate cards report"
	@echo "make clean          - Remove venv and cache files"

venv:
	python3.12 -m venv venv

install:
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

install-dev:
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install pytest black flake8

scrape-legacy:
	. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/scrape_legacy.py

analyze-hate:
	. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/analyze_hate_cards.py

generate-pdf:
	. venv/bin/activate && PYTHONPATH=$(PWD) python scripts/generate_pdf_report.py

clean:
	rm -rf venv __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
