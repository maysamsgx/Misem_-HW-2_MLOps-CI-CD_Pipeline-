# ==================================
# Stage 1: Builder
# ==================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building packages (if any)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Install python dependencies to a temporary location
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ==================================
# Stage 2: Final Runtime
# ==================================
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Ensure scripts are in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy source code
COPY src/ src/
COPY models/ models/

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check (Docker native)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI app
CMD ["uvicorn", "src.inference:app", "--host", "0.0.0.0", "--port", "8000"]
