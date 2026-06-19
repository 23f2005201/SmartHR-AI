# Stage 1: Build virtual dependencies environment safely
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a localized wheel repository
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Minimal runtime image execution footprint
FROM python:3.11-slim AS runner

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python path dependencies from builder stage
COPY --from=builder /root/.local /root/.local
COPY . /workspace

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]