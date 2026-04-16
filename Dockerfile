# Dockerfile optimizado para Trading MVP en Coolify
# Basado en mejores prácticas de LobeHub Python Deployment Skill

FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema necesarias
# libpq-dev para PostgreSQL, build-essential para compilaciones
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache de Docker)
COPY requirements.txt .

# Instalar el paquete trading-mvp en modo editable
# Esto instala todas las dependencias y hace que trading_mvp esté disponible
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Copiar el resto del código
COPY . .

# Crear directorio de logs
RUN mkdir -p /app/logs

# NO exponer puertos - es un script de trading, no un web server
# EXPOSE 8000  # Comentado - no necesitamos exponer puertos

# Health check para que Coolify sepa que el contenedor está vivo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD test -f /app/.venv/bin/python || exit 1

# Comando de inicio - mantener el contenedor vivo
CMD ["tail", "-f", "/dev/null"]