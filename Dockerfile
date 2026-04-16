# Coolify Python Deployment - Trading MVP
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create a startup script that handles both manual runs and cron
RUN echo '#!/bin/bash\n\
if [ "$1" = "cron" ]; then\n\
    echo "Starting Investment Desk in Cron Mode..."\n\
    AUTOPILOT_MODE=on python ejecutar_mesa_inversiones\n\
elif [ "$1" = "manual" ]; then\n\
    echo "Starting Investment Desk in Manual Mode..."\n\
    AUTOPILOT_MODE=off python ejecutar_mesa_inversiones\n\
else\n\
    echo "Usage: docker run [image] [cron|manual]"\n\
    echo "  - cron: Run with AUTOPILOT_MODE=on (for automated execution)"\n\
    echo "  - manual: Run with AUTOPILOT_MODE=off (for testing)"\n\
    exit 1\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30m --timeout=5m --start-period=1m --retries=3 \
    CMD python -c "import requests; print('OK')" || exit 1

# NO ejecutar nada por defecto - Solo mantener contenedor vivo para CRON jobs
# El contenedor SOLO se ejecutará cuando los CRON jobs de Coolify lo disparen
CMD ["tail", "-f", "/dev/null"]