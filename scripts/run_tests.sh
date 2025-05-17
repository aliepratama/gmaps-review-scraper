#!/usr/bin/env bash
# Run all pytest tests
poetry run pytest --maxfail=1 --disable-warnings -q
