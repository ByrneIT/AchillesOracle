## Multi-stage build: compile dependencies in builder and produce small runtime image
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Build dependencies for packages that need compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel
# Install runtime deps into /install so final image stays small
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy source for completeness (some packages may inspect package files)
COPY . /app

## Final runtime image
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1
ENV PATH=/install/bin:$PATH

# Create a non-root user for running the app
RUN groupadd -r app && useradd -r -g app -d /home/app -s /sbin/nologin app \
    && mkdir -p /home/app

# Copy installed packages and application code from builder
COPY --from=builder /install /install
COPY --from=builder /app /app

# Set permissions and working dir
RUN chown -R app:app /app /install
WORKDIR /app

# Drop to non-root user
USER app

EXPOSE 8000

# Lightweight healthcheck without adding curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD python -c "import urllib.request,sys;res=urllib.request.urlopen('http://127.0.0.1:8000/health');sys.exit(0 if res.status==200 else 1)"

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
