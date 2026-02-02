FROM python:3.12-slim

# Install system dependencies (GTK/WeasyPrint, OCR, Chromium for Kaleido)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libgl1 \
    libglib2.0-0 \
    chromium \
    chromium-driver \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
  && rm -rf /var/lib/apt/lists/*

# Set Chrome path for Kaleido
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMIUM_PATH=/usr/bin/chromium

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "Home.py"]

