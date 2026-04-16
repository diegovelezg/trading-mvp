# 🚀 Despliegue en VPS con Coolify

## 🎯 CONFIGURACIÓN RECOMENDADA: UI DE COOLIFY

**INSTRUCCIONES COMPLETAS**: Ver `COOLIFY_CONFIG.md` para configuración paso a paso en la UI de Coolify.

## 📋 Resumen de Configuración en Coolify UI:

### ⏰ Horarios de Ejecución

| Ejecución | EST | UTC | **Lima** | Propósito |
|-----------|-----|-----|----------|-----------|
| **Pre-Market** | 08:30 AM | 12:30 | **07:30 AM** | Gaps + Apertura |
| **Power Hour** | 15:00 PM | 19:00 | **14:00 PM** | Cierre + Smart Money |

### 🔧 Pasos de Despliegue

#### 1. Preparar el Entorno

```bash
# Clonar el repositorio en tu VPS
cd /path/to/your/vps/directory
git clone <your-repo-url> trading-mvp
cd trading-mvp

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Configurar Variables de Entorno

Copia y renombra el archivo de entorno:

```bash
cp .env.example coolify/.env
```

Edita `coolify/.env` con tus credenciales reales:

```bash
# Alpaca (Paper Trading)
ALPACA_PAPER_API_KEY=tu_key_aqui
PAPER_API_SECRET=tu_secret_aqui
ALPACA_PAPER_BASE_URL=https://paper-api.alpaca.markets/v2

# Alpaca (Data API)
ALPACA_DATA_API_KEY=tu_data_key_aqui
DATA_API_SECRET=tu_data_secret_aqui
ALPACA_DATA_BASE_URL=https://api.alpaca.markets

# Gemini AI
GEMINI_API_KEY=tu_gemini_key_aqui
GEMINI_API_MODEL_01=gemini-2.0-flash-exp
GEMINI_API_MODEL_02=gemini-2.0-flash-exp

# Supabase
NEXT_PUBLIC_SUPABASE_URL=tu_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu_supabase_anon_key

# News API
SERPAPI_API_KEY=tu_serpapi_key_aqui

# Control de Autopilot
AUTOPILOT_MODE=on

# Risk Management
MIN_CONFIDENCE_SCORE=0.75
MAX_POSITION_SIZE_PCT=0.10
MAX_PORTFOLIO_EXPOSURE_PCT=0.85
MIN_CASH_RESERVE_PCT=0.15
DAILY_DRAWDOWN_LIMIT_PCT=0.03
```

#### 3. Configurar Cron Jobs

Edita el crontab:

```bash
crontab -e
```

Agrega estas líneas:

```bash
# Investment Desk - Pre-Market (07:30 AM Lima | 12:30 UTC)
30 12 * * 1-5 cd /path/to/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_pre.log 2>&1

# Investment Desk - Power Hour (14:00 PM Lima | 19:00 UTC)
0 19 * * 1-5 cd /path/to/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_power.log 2>&1
```

**⚠️ IMPORTANTE**: Reemplaza `/path/to/trading-mvp` con la ruta real en tu VPS.

#### 4. Crear Directorio de Logs

```bash
mkdir -p logs
chmod 755 logs
```

#### 5. Verificar Configuración

```bash
# Test manual del script
cd /path/to/trading-mvp
AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones
```

## 📊 Monitoreo

### Ver Logs

```bash
# Logs de Pre-Market
tail -f logs/investment_desk_pre.log

# Logs de Power Hour
tail -f logs/investment_desk_power.log

# Logs principales del sistema
tail -f investment_desk.log
```

### Ver Última Ejecución

```bash
python scripts/fetch_latest_execution_data.py
```

### Ver Decisiones Recientes

```bash
python scripts/manage_decisions.py --list-recent
```

## 🛡️ Seguridad

- ✅ El `.env` con credenciales NUNCA debe ir a Git
- ✅ Usar siempre `AUTOPILOT_MODE=off` para testing
- ✅ Verificar que el Risk Management esté configurado correctamente
- ✅ Monitorear los logs regularmente

## 🚨 Troubleshooting

### El cron no se ejecuta

1. Verificar que la ruta en el crontab sea correcta
2. Verificar que el archivo `ejecutar_mesa_inversiones.py` tenga permisos de ejecución
3. Revisar logs del sistema: `sudo tail -f /var/log/syslog`

### Errores de conexión

1. Verificar que las credenciales en `coolify/.env` sean correctas
2. Verificar conexión a Alpaca API
3. Verificar conexión a Supabase

### AutoPilot no ejecuta órdenes

1. Verificar que `AUTOPILOT_MODE=on` esté en el comando del cron
2. Revisar los límites de Risk Management en el `.env`
3. Verificar que la cuenta de Alpaca Paper tenga fondos

## 📞 Soporte

Si encuentras problemas, revisa:
- Logs: `investment_desk.log`
- Documentación principal: `README.md`
- Issues del repositorio