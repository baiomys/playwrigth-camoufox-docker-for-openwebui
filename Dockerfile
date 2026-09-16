FROM python:3.11-slim

# 1. Системные зависимости Linux для работы Firefox / Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxcb1 libxkbcommon0 libx11-6 \
    libxcomposite1 libxdamage1 libxext6 libxfixes3 librandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 2. Фиксируем пути и вывод логов
ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# 3. Устанавливаем Camoufox и Playwright
RUN pip install --no-cache-dir "camoufox[geoip]" playwright

# 4. Предварительно скачиваем бинарники браузера прямо при сборке образа
RUN python -m camoufox fetch

EXPOSE 9222

# 5. Запускаем нативный встроенный WebSocket-сервер Camoufox
CMD ["python", "-m", "camoufox", "server", "--host", "0.0.0.0", "--port", "9222"]
