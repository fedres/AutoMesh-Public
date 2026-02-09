# Multi-stage Docker build for MeshMind-AFID
# Stage 1: Base image with dependencies
FROM python:3.12-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/base.txt /app/requirements/base.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt

# Stage 2: Application
FROM base as app

# Copy source code
COPY src/ /app/src/
COPY assets/ /app/assets/
COPY pyproject.toml /app/
COPY README.md /app/

# Install package
RUN pip install -e .

# Set environment
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["meshmind-cli", "--help"]
