#!/bin/bash

# =====================================================================
# CONFIGURACIÓN DE CRON JOBS PARA TRADING MVP
# =====================================================================

echo "🚀 Configurando Cron Jobs para Trading MVP..."
echo ""

# Solicitar la ruta del proyecto
read -p "📍 Ingresa la ruta completa del proyecto (ej: /home/user/trading-mvp): " PROJECT_PATH

# Validar que la ruta existe
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Error: La ruta $PROJECT_PATH no existe"
    exit 1
fi

echo "✅ Ruta válida: $PROJECT_PATH"
echo ""

# Crear directorio de logs si no existe
echo "📝 Creando directorio de logs..."
mkdir -p "$PROJECT_PATH/logs"
chmod 755 "$PROJECT_PATH/logs"
echo "✅ Directorio de logs creado"
echo ""

# Confirmar configuración
echo "⏰ Se configurarán los siguientes cron jobs:"
echo ""
echo "1. Pre-Market Analysis:"
echo "   - Horario: 07:30 AM Lima (12:30 UTC)"
echo "   - Días: Lunes a Viernes"
echo "   - Log: logs/investment_desk_pre.log"
echo ""
echo "2. Power Hour Analysis:"
echo "   - Horario: 14:00 PM Lima (19:00 UTC)"
echo "   - Días: Lunes a Viernes"
echo "   - Log: logs/investment_desk_power.log"
echo ""
read -p "¿Deseas continuar? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "❌ Configuración cancelada"
    exit 0
fi

echo ""
echo "📝 Agregando cron jobs..."

# Crear archivo temporal con los cron jobs
CRON_FILE=$(mktemp)

# Backup del crontab actual
crontab -l > "$PROJECT_PATH/crontab_backup_$(date +%Y%m%d_%H%M%S)" 2>/dev/null

# Agregar los nuevos cron jobs
cat > "$CRON_FILE" << EOL

# Trading MVP - Investment Desk Auto-Run
# Pre-Market Analysis (07:30 AM Lima | 12:30 UTC)
30 12 * * 1-5 cd $PROJECT_PATH && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_pre.log 2>&1

# Power Hour Analysis (14:00 PM Lima | 19:00 UTC)
0 19 * * 1-5 cd $PROJECT_PATH && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_power.log 2>&1
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
echo "  - Backup guardado en: $PROJECT_PATH/crontab_backup_*"
echo ""
echo "🎯 Próxima ejecución programada:"
echo "  - Pre-Market: Mañana a las 07:30 AM (Lima)"
echo "  - Power Hour: Mañana a las 14:00 PM (Lima)"
echo ""