#How to use:
#Run all tests + coverage report:
#make test
#Run tests and open HTML coverage report:
#make coverage-html
#Clean coverage data:
#make clean



.PHONY: test clean coverage-html

# Default target: run tests with coverage
test:
	python run_tests.py

# Run tests and open coverage HTML report in browser (Linux/macOS)
coverage-html: test
	@if command -v xdg-open > /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open > /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo "Open htmlcov/index.html manually to view coverage report"; \
	fi

# Clean coverage files and caches
clean:
	rm -rf .coverage htmlcov
