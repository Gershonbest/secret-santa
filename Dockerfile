# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./

# Install build tools and Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir fastapi "uvicorn[standard]" sqlalchemy jinja2 python-multipart "passlib[bcrypt]" "python-jose[cryptography]" python-dotenv psycopg2-binary

# Copy application code
COPY . .

# Expose port (Render will set PORT environment variable)
EXPOSE 8000

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

