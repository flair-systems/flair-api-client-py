# Makefile for flair-api-client-py

.PHONY: build test clean dist release install

# Build the package
build:
	python -m build

# Run tests
test:
	python -m pytest test_flair_api.py -v

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