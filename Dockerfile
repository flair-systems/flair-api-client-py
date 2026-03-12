FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml pyproject.toml
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import flair_api; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "flair_api"]
