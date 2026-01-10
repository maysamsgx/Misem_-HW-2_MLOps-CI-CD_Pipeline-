# ==================================
# Stage 1: Builder
# ==================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
# Install python dependencies
COPY requirements-prod.txt .
RUN pip install --user --no-cache-dir -r requirements-prod.txt

# ==================================
# Stage 2: Final Runtime
# ==================================
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages
COPY --from=builder /root/.local /home/appuser/.local

# Ensure scripts are in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy source code
COPY src/ src/
COPY models/ models/

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check (Python-based, no curl dependency)
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run FastAPI app
CMD ["python", "-m", "src.inference"]
