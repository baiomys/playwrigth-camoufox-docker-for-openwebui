FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# 1. Минимально необходимые утилиты для скачивания
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget \
    && rm -rf /var/lib/apt/lists/*

# 2. Устанавливаем Python-пакеты
RUN pip install --no-cache-dir "camoufox[geoip]" playwright

# 3. Автоматически устанавливаем системные зависимости для Firefox и скачиваем Camoufox
RUN playwright install-deps firefox \
    && python -m camoufox fetch

EXPOSE 9222

# 4. Запускаем нативный WebSocket-сервер Camoufox
CMD ["python", "-m", "camoufox", "server", "--host", "0.0.0.0", "--port", "9222"]
