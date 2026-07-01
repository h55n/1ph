FROM python:3.11-slim

WORKDIR /app

# System dependencies for playwright/firefox
RUN apt-get update && apt-get install -y \
    wget curl gnupg \
    libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Only install Firefox if enough RAM (detected at runtime)
ARG INSTALL_BROWSER=false
RUN if [ "$INSTALL_BROWSER" = "true" ]; then playwright install firefox; fi

COPY . .

EXPOSE 8765

CMD ["zerocrawl", "serve", "--host", "0.0.0.0", "--port", "8765"]
