FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    CAMOUFOX_PORT=9222 \
    CAMOUFOX_WS_PATH=playwright

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "camoufox[geoip]" \
    "playwright==1.62.0"

RUN playwright install-deps firefox \
    && python -m camoufox fetch

COPY start.py /app/start.py

EXPOSE 9222

CMD ["python", "/app/start.py"]

