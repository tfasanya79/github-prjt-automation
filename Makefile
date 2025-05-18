# How to use:
# Run all tests + coverage report:         make test
# Run tests and open HTML coverage:        make coverage-html
# Clean coverage data and __pycache__:     make clean
# Lint with ruff:                          make lint
# Type check with mypy:                    make typecheck
# Run all checks (lint, typecheck, test):  make all

.PHONY: test clean coverage-html lint typecheck all

# Default target: run tests with coverage
test:
	@echo "Running tests with coverage..."
	PYTHONPATH=src coverage run -m unittest discover -s tests -v
	coverage report
	coverage xml

# Run tests and open coverage HTML report
coverage-html: test
	@coverage html
	@if command -v xdg-open > /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open > /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo "Open htmlcov/index.html manually to view coverage report"; \
	fi

# Clean build/test artifacts
clean:
	@echo "Cleaning up..."
	rm -rf .coverage htmlcov __pycache__ .mypy_cache .ruff_cache

# Lint the codebase using Ruff
lint:
	@echo "Linting with Ruff..."
	ruff src tests

# Type checking using mypy
typecheck:
	@echo "Type checking with mypy..."
	mypy src tests

# Run all quality checks
all: lint typecheck test
