# Backend Dockerfile - Python + R with CopyKAT
# Multi-stage build for optimized image size

FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install R and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libgit2-dev \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory - create project structure
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install R packages (BiocManager and CopyKAT)
# This takes a while but is cached
RUN R -e "install.packages('BiocManager', repos='https://cloud.r-project.org')" && \
    R -e "BiocManager::install('copykat', ask=FALSE, update=FALSE)" && \
    R -e "install.packages(c('yaml', 'logger'), repos='https://cloud.r-project.org')"

# Copy application code to backend directory to maintain project structure
COPY . /app/backend/

# Create directories for data and results
RUN mkdir -p /app/backend/data/uploads /app/backend/data/raw /app/backend/results

# Set environment variables for R executor (Docker mode - no conda)
ENV DOCKER_MODE=true \
    R_EXECUTABLE=Rscript \
    PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/files || exit 1

# Run the application from project root
WORKDIR /app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

