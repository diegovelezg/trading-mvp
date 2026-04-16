# 🔧 Configuración de Coolify para Trading MVP

## ⚠️ Configuración Actual (INCORRECTA):
- ❌ **"Is it a static site?"** - NO es un sitio estático
- ❌ **Port: 3000** - NO expone ningún puerto
- ❌ **Start Command** - No tiene un comando válido
- ❌ **Estado: "Exited"** - Se cierra inmediatamente

## ✅ Configuración Correcta para Trading Python:

### 1. GENERAL CONFIGURATION

#### Name:
```
trading-mvp-python
```

#### Build Pack:
```
Nixpacks
```

#### ⚠️ **IMPORTANT**: Desmarcar "Is it a static site?"

#### Ports Exposes:
```
Dejar VACÍO (no expone ningún puerto)
```

#### Base Directory:
```
/
```

#### Install Command:
```bash
# Opción 1: Si detecta automáticamente
python3 -m venv .venv && .venv/bin/pip install --upgrade pip

# Opción 2: Manual
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

#### Build Command:
```bash
# OPCIÓN A - Simple (con setup.py creado):
pip install -e .

# OPCIÓN B - Sin setup.py:
.venv/bin/pip install -r requirements.txt
```

#### Start Command:
```bash
# Mantener el contenedor vivo sin servidor web
tail -f /dev/null
```

---

### 2. ENVIRONMENT VARIABLES

Copia estas variables en la sección "Environment Variables":

```bash
# Alpaca Trading (Paper Trading)
ALPACA_PAPER_API_KEY=YOUR_ALPACA_PAPER_API_KEY
PAPER_API_SECRET=YOUR_ALPACA_SECRET_KEY
ALPACA_PAPER_BASE_URL=https://paper-api.alpaca.markets/v2

# Alpaca Data API
ALPACA_DATA_API_KEY=YOUR_ALPACA_DATA_API_KEY
DATA_API_SECRET=YOUR_ALPACA_SECRET_KEY
ALPACA_DATA_BASE_URL=https://api.alpaca.markets

# Gemini AI
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_API_MODEL_01=gemini-2.0-flash-exp
GEMINI_API_MODEL_02=gemini-2.0-flash-exp
GEMINI_API_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_API_EMBEDDING_SIZE=768

# Z.ai AI (Alternative)
ZAI_API_MODEL_01=glm-5.1
ZAI_API_KEY=YOUR_ZAI_API_KEY

# SerpAPI (News)
SERPAPI_API_KEY=YOUR_SERPAPI_API_KEY

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-supabase-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
DATABASE_URL=postgresql://postgres.dev_tenant:YOUR_DATABASE_PASSWORD@YOUR_DATABASE_HOST:6544/postgres

# System Config
AUTOPILOT_MODE=on

# Risk Management
MAX_TRADES_PER_DAY=10
MAX_PORTFOLIO_EXPOSURE_PCT=0.85
MIN_CASH_RESERVE_PCT=0.15
MAX_POSITION_SIZE_PCT=0.10
MIN_CONFIDENCE_SCORE=0.75
DAILY_DRAWDOWN_LIMIT_PCT=0.03

# Python Path (CRÍTICO para encontrar el módulo trading_mvp)
PYTHONPATH=/app:/app/scripts
```

---

### 3. SCHEDULED TASKS (CRON JOBS)

En la sección **"Scheduled Tasks"** del servicio en Coolify:

#### Task 1: Pre-Market Analysis
```bash
Command: python ejecutar_mesa_inversiones
# O alternativamente: /opt/venv/bin/python ejecutar_mesa_inversiones
Cron: 30 12 * * 1-5
Description: Investment Desk Pre-Market (07:30 AM Lima | 12:30 UTC)
```

#### Task 2: Power Hour Analysis
```bash
Command: python ejecutar_mesa_inversiones
# O alternativamente: /opt/venv/bin/python ejecutar_mesa_inversiones
Cron: 0 19 * * 1-5
Description: Investment Desk Power Hour (14:00 PM Lima | 19:00 UTC)
```

---

### 4. PERSISTENT STORAGE (Opcional pero recomendado)

Para mantener los logs:

#### Mount:
```bash
logs -> /app/logs
```

---

## 🚀 PASO A PASO EN LA UI DE COOLIFY:

### 1. **General Tab**
   - Cambiar "Name" a: `trading-mvp-python`
   - **Desmarcar** "Is it a static site?"
   - **Borrar** "Ports Exposes" (dejar vacío)
   - En "Install Command":
     ```bash
     python3 -m venv .venv && .venv/bin/pip install --upgrade pip
     ```
   - En "Build Command":
     ```bash
     .venv/bin/pip install -r requirements.txt
     ```
   - En "Start Command":
     ```bash
     tail -f /dev/null
     ```
   - Click **"Save"**

### 2. **Environment Variables Tab**
   - Copiar TODAS las variables de arriba
   - Click **"Save"**

### 3. **Scheduled Tasks Tab**
   - Agregar Task 1 (Pre-Market)
   - Agregar Task 2 (Power Hour)
   - Click **"Save"**

### 4. **Deploy!**
   - Click en el botón **"Deploy"** en la parte superior
   - El contenedor debería quedar en estado **"Running"** (no "Exited")

---

## 📊 Verificar Funcionamiento:

### 1. Ver Logs del Contenedor:
```bash
# En la UI de Coolify, ve a "Logs" del servicio
# Deberías ver algo como:
# "Container is healthy and running"
```

### 2. Ver Logs de las Ejecuciones:
```bash
# En el terminal del contenedor (Coolify -> Terminal)
ls -la logs/

# Deberías ver:
# - investment_desk_pre.log (después de la 1ra ejecución)
# - investment_desk_power.log (después de la 2da ejecución)
```

### 3. Test Manual:
```bash
# En el terminal del contenedor
.venv/bin/python ejecutar_mesa_inversiones
```

---

## 🎯 Expected Behavior:

1. **Contenedor**: Siempre en estado "Running" 🟢
2. **Scheduled Tasks**: Se ejecutan automáticamente según el cron
3. **Logs**: Se generan en `/app/logs/`
4. **Trading**: AutoPilot ejecuta órdenes si se cumplen las condiciones

---

## 🚨 Troubleshooting:

### Si el contenedor sigue en "Exited":
1. Verificar que el "Start Command" sea: `tail -f /dev/null`
2. Revisar los logs del contenedor en la UI de Coolify
3. Verificar que el "Build Command" instaló las dependencias correctamente

### Si las tareas no se ejecutan:
1. Verificar que los cron expressions estén correctos
2. Verificar que el comando sea: `.venv/bin/python ejecutar_mesa_inversiones`
3. Revisar logs de Coolify para ver errores de ejecución

### Si hay errores de importación:
1. Verificar que `PYTHONPATH` incluya las rutas correctas
2. Verificar que el virtual environment se creó correctamente
3. Revisar que `requirements.txt` se instaló sin errores