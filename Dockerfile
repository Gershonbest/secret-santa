# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files (pyproject.toml and uv.lock if it exists)
COPY pyproject.toml ./
COPY uv.lock* ./

# Copy routers package (needed for package build)
COPY routers/ ./routers/

# Install Python dependencies using uv sync (reads from pyproject.toml)
RUN uv sync --frozen --no-dev

# Copy rest of application code
COPY . .

# Expose port (Render will set PORT environment variable)
EXPOSE 8000

# Run the application using uv run
CMD uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

