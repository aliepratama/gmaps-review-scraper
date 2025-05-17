#!/usr/bin/env bash
# Lint code with flake8 and type-check with mypy
poetry run flake8 src/reviewscraper
poetry run mypy src/reviewscraper
