# Makefile for flair-api-client-py

.PHONY: build test clean dist release install

# Build the package
build:
	python -m build

# Run tests
test: test-unit

test-unit:
	python -m pytest test_mock_api.py -v

test-integration:
	python -m pytest test_real_api.py -v

test-all: test-unit test-integration

test-coverage:
	python -m pytest test_mock_api.py --cov=flair_api --cov-report=html

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/

# Create distribution files
dist: clean build

# Install in development mode
install:
	pip install -e .

# Release to PyPI (requires twine)
release: dist
	twine upload dist/*

# Release to TestPyPI (requires twine)
test-release: dist
	twine upload --repository testpypi dist/*