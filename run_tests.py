import coverage
import unittest
import sys
import argparse

def run_tests_with_coverage(test_path='tests'):
    """
    Run unittests with coverage measurement.

    Args:
        test_path (str): Path or pattern for tests to run. Defaults to 'tests'.
    """
    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()

    # Load tests, either by discovery or by specific path/module
    loader = unittest.TestLoader()
    try:
        suite = loader.discover(start_dir=test_path)
    except Exception:
        # If discover fails, try loading test directly (e.g., test module or case)
        suite = loader.loadTestsFromName(test_path)

    # Run tests with verbosity=2 for detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Stop coverage and save results
    cov.stop()
    cov.save()

    # Print coverage report to console
    print("\nCoverage report:")
    cov.report(show_missing=True)

    # Generate HTML coverage report
    cov.html_report(directory='htmlcov')
    print("\nHTML coverage report generated at htmlcov/index.html")

    # Exit with appropriate status code for CI or shell
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run unittests with coverage reporting.")
    parser.add_argument(
        'test_path', nargs='?', default='tests',
        help="Test directory, module or specific test case (default: 'tests')"
    )
    args = parser.parse_args()
    run_tests_with_coverage(args.test_path)
