# -------------------------------
# STAGE 1: Builder (install deps)
# -------------------------------
FROM python:3.11-slim AS builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for compiling packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# ✅ Copy only requirements first (for Docker caching)
COPY requirements.txt .

# ✅ Install Python dependencies in a temp folder (wheel format)
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# -------------------------------
# STAGE 2: Final runtime image
# -------------------------------
FROM python:3.11-slim

# Set environment variables for runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install only minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# ✅ Copy prebuilt Python wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# ✅ Install from wheels (faster & smaller)
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy the actual project
COPY backend /app

# ✅ Expose FastAPI port
EXPOSE 8000

# ✅ Default command (only for backend container)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
