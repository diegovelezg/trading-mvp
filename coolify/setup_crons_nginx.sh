#!/bin/bash

# =====================================================================
# CONFIGURACIÓN DE CRON JOBS PARA COOLIFY NGINX
# =====================================================================

echo "🚀 Configurando Cron Jobs para Trading MVP en Coolify (Nginx)..."
echo ""

# Detectar la ruta del proyecto (asumimos que estamos en ella)
PROJECT_PATH="$(pwd)"
echo "📍 Ruta detectada: $PROJECT_PATH"

# Validar que estamos en el proyecto correcto
if [ ! -f "ejecutar_mesa_inversiones.py" ]; then
    echo "❌ Error: No se encuentra ejecutar_mesa_inversiones.py"
    echo "   Por favor ejecuta este script desde la raíz del proyecto"
    exit 1
fi

echo "✅ Proyecto validado"
echo ""

# Crear directorio de logs si no existe
echo "📝 Creando directorio de logs..."
mkdir -p "$PROJECT_PATH/logs"
chmod 755 "$PROJECT_PATH/logs"
echo "✅ Directorio de logs creado"
echo ""

# Detectar si hay entorno virtual
PYTHON_CMD=""
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
    echo "🐍 Entorno virtual detectado: .venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
    echo "🐍 Entorno virtual detectado: venv/bin/python"
else
    PYTHON_CMD="/usr/bin/python3"
    echo "🐍 Usando Python del sistema: /usr/bin/python3"
fi
echo ""

# Confirmar configuración
echo "⏰ Se configurarán los siguientes cron jobs:"
echo ""
echo "1. Pre-Market Analysis:"
echo "   - Horario: 07:30 AM Lima (12:30 UTC)"
echo "   - Días: Lunes a Viernes"
echo "   - Comando: cd $PROJECT_PATH && AUTOPILOT_MODE=on $PYTHON_CMD ejecutar_mesa_inversiones"
echo "   - Log: logs/investment_desk_pre.log"
echo ""
echo "2. Power Hour Analysis:"
echo "   - Horario: 14:00 PM Lima (19:00 UTC)"
echo "   - Días: Lunes a Viernes"
echo "   - Comando: cd $PROJECT_PATH && AUTOPILOT_MODE=on $PYTHON_CMD ejecutar_mesa_inversiones"
echo "   - Log: logs/investment_desk_power.log"
echo ""
read -p "¿Deseas continuar? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "❌ Configuración cancelada"
    exit 0
fi

echo ""
echo "📝 Agregando cron jobs..."

# Backup del crontab actual
BACKUP_FILE="$PROJECT_PATH/crontab_backup_$(date +%Y%m%d_%H%M%S)"
crontab -l > "$BACKUP_FILE" 2>/dev/null
echo "📦 Backup guardado en: $BACKUP_FILE"

# Crear archivo temporal con los cron jobs
CRON_FILE=$(mktemp)

# Obtener el crontab actual (si existe)
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    cat "$BACKUP_FILE" > "$CRON_FILE"
    echo "" >> "$CRON_FILE"
fi

# Agregar los nuevos cron jobs
cat >> "$CRON_FILE" << EOL

# Trading MVP - Investment Desk Auto-Run (Coolify Nginx)
# Pre-Market Analysis (07:30 AM Lima | 12:30 UTC)
30 12 * * 1-5 cd $PROJECT_PATH && AUTOPILOT_MODE=on $PYTHON_CMD ejecutar_mesa_inversiones >> $PROJECT_PATH/logs/investment_desk_pre.log 2>&1

# Power Hour Analysis (14:00 PM Lima | 19:00 UTC)
0 19 * * 1-5 cd $PROJECT_PATH && AUTOPILOT_MODE=on $PYTHON_CMD ejecutar_mesa_inversiones >> $PROJECT_PATH/logs/investment_desk_power.log 2>&1
EOL

# Instalar el nuevo crontab
crontab "$CRON_FILE"

# Limpiar archivo temporal
rm "$CRON_FILE"

echo "✅ Cron jobs configurados exitosamente"
echo ""

# Mostrar el crontab actual
echo "📋 Crontab actual:"
echo "=========================================="
crontab -l
echo "=========================================="
echo ""

echo "✅ Configuración completada!"
echo ""
echo "📝 Comandos útiles:"
echo "  - Ver logs Pre-Market: tail -f $PROJECT_PATH/logs/investment_desk_pre.log"
echo "  - Ver logs Power Hour: tail -f $PROJECT_PATH/logs/investment_desk_power.log"
echo "  - Ver crontab: crontab -l"
echo "  - Editar crontab: crontab -e"
echo "  - Ver logs del sistema: sudo tail -f /var/log/syslog | grep CRON"
echo ""
echo "🎯 Próxima ejecución programada:"
echo "  - Pre-Market: Mañana a las 07:30 AM (Lima)"
echo "  - Power Hour: Mañana a las 14:00 PM (Lima)"
echo ""

# Test manual del script (opcional)
read -p "¿Deseas ejecutar un test manual ahora? (y/n): " RUN_TEST
if [ "$RUN_TEST" = "y" ]; then
    echo ""
    echo "🧪 Ejecutando test manual..."
    echo "=========================================="
    cd "$PROJECT_PATH" && AUTOPILOT_MODE=on $PYTHON_CMD ejecutar_mesa_inversiones
    echo "=========================================="
    echo ""
    echo "✅ Test completado. Revisa los logs arriba"
fi
