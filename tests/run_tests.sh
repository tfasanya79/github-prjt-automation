#!/bin/bash
# run_tests.sh - Run unittest discovery with coverage and generate reports

echo "Running tests with coverage..."
coverage run -m unittest discover -v

echo "Showing coverage report:"
coverage report -m

echo "Generating HTML coverage report..."
coverage html

echo "Done. Open htmlcov/index.html in your browser to view the coverage details."
