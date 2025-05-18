import coverage
import unittest
import sys

def run_tests_with_coverage():
    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()

    # Report coverage
    print("\nCoverage report:")
    cov.report(show_missing=True)

    # Generate HTML report
    cov.html_report(directory='htmlcov')
    print("\nHTML coverage report generated in 'htmlcov' directory.")

    # Exit with appropriate status code (0 if all tests passed)
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    run_tests_with_coverage()
