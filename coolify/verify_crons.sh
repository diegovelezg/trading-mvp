#!/bin/bash

# =====================================================================
# VERIFICACIÓN DE CRON JOBS EN COOLIFY
# =====================================================================

echo "🔍 Verificando configuración de Cron Jobs..."
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar estado
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        return 1
    fi
}

echo "1️⃣  Verificando archivos de configuración..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar Dockerfiles
files_to_check=(
    "Dockerfile.coolify"
    "Dockerfile.coolify-cron"
    "docker-compose.coolify.yml"
    "ejecutar_mesa_inversiones.py"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file existe"
    else
        echo -e "${RED}✗${NC} $file NO existe"
    fi
done

echo ""
echo "2️⃣  Verificando configuración de Cron en Dockerfiles..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar si Dockerfile.coolify-cron tiene configuración de cron
if [ -f "Dockerfile.coolify-cron" ]; then
    if grep -q "cron" Dockerfile.coolify-cron; then
        echo -e "${GREEN}✓${NC} Dockerfile.coolify-cron tiene configuración de cron"
    else
        echo -e "${YELLOW}⚠${NC}  Dockerfile.coolify-cron no tiene configuración de cron"
    fi

    # Mostrar cron jobs configurados
    echo ""
    echo "📋 Cron jobs configurados en Dockerfile.coolify-cron:"
    grep -A 2 "echo.*30 12" Dockerfile.coolify-cron | sed 's/echo //g' | sed 's/"//g' | sed 's/\\//g'
fi

echo ""
echo "3️⃣  Verificando variables de entorno necesarias..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

required_vars=(
    "AUTOPILOT_MODE"
    "DATABASE_URL"
    "GEMINI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if grep -q "$var" .env 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $var está configurada en .env"
    else
        echo -e "${RED}✗${NC} $var NO está configurada en .env"
    fi
done

echo ""
echo "4️⃣  Verificando directorio de logs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "logs" ]; then
    echo -e "${GREEN}✓${NC} Directorio logs existe"
    ls -la logs/ 2>/dev/null | tail -n +4 | head -5
else
    echo -e "${YELLOW}⚠${NC}  Directorio logs NO existe (se creará automáticamente)"
    mkdir -p logs
    echo -e "${GREEN}✓${NC} Directorio logs creado"
fi

echo ""
echo "5️⃣  Instrucciones para Coolify..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📋 OPCIÓN 1: Usar Cron Jobs Nativos de Coolify"
echo "   1. En la interfaz de Coolify, ve a tu aplicación"
echo "   2. Ve a la pestaña 'Cron Jobs'"
echo "   3. Agrega estos cron jobs:"
echo ""
echo "   # Pre-Market (07:30 AM Lima | 12:30 UTC)"
echo "   30 12 * * 1-5 cd /app && python ejecutar_mesa_inversiones >> /app/logs/investment_desk_pre.log 2>&1"
echo ""
echo "   # Power Hour (14:00 PM Lima | 19:00 UTC)"
echo "   0 19 * * 1-5 cd /app && python ejecutar_mesa_inversiones >> /app/logs/investment_desk_power.log 2>&1"
echo ""

echo "📋 OPCIÓN 2: Usar Dockerfile con Cron Integrado"
echo "   1. Usa el Dockerfile: Dockerfile.coolify-cron"
echo "   2. Este Dockerfile instala y configura cron automáticamente"
echo "   3. Los cron jobs se ejecutarán dentro del contenedor"
echo ""

echo "📋 OPCIÓN 3: Usar docker-compose"
echo "   1. Usa el archivo: docker-compose.coolify.yml"
echo "   2. Este archivo tiene dos servicios:"
echo "      - trading-mvp: Servicio principal"
echo "      - trading-cron: Servicio con cron integrado"
echo ""

echo "6️⃣  Comandos útiles para verificación..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Ver logs de cron en tiempo real:"
echo "   tail -f logs/investment_desk_pre.log"
echo "   tail -f logs/investment_desk_power.log"
echo ""
echo "🐳 Verificar que cron está corriendo en el contenedor:"
echo "   docker exec <container_id> cron ps"
echo ""
echo "📋 Ver crontab del contenedor:"
echo "   docker exec <container_id> crontab -l"
echo ""
echo "📊 Ver todos los logs del contenedor:"
echo "   docker logs -f <container_id>"
echo ""

echo "✅ Verificación completada!"
echo ""