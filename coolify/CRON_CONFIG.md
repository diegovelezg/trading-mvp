# 🚨 IMPORTANTE - Contenedor NO debe ejecutar continuamente

## ❌ LO QUE ESTABA PASANDO:
- Dockerfile tenía: `CMD ["python", "ejecutar_mesa_inversiones.py"]`
- Coolify ejecutaba el contenedor → intentaba correr el script → **FALLABA** sin env vars
- El contenedor se reiniciaba en bucle infinito

## ✅ LO QUE DEBE PASAR:
- Contenedor **SOLO se mantiene vivo** (sin ejecutar el script)
- **CRON jobs de Coolify** ejecutan el script en horarios específicos
- **Cero ejecuciones fuera de los horarios programados**

## 🔧 Configuración Correcta en Coolify:

### 1. Dockerfile
```dockerfile
# NO ejecutar el script por defecto
CMD ["tail", "-f", "/dev/null"]
```

### 2. CRON Jobs en Coolify
En **Advanced Settings → Cron Jobs**, agregar:

```bash
# Pre-Market (07:30 AM Lima | 12:30 UTC)
30 12 * * 1-5 cd /app && python ejecutar_mesa_inversiones.py >> /app/logs/investment_desk_pre.log 2>&1

# Power Hour (14:00 PM Lima | 19:00 UTC)
0 19 * * 1-5 cd /app && python ejecutar_mesa_inversiones.py >> /app/logs/investment_desk_power.log 2>&1
```

### 3. Variables de Entorno
Configurar **TODAS** las variables antes del primer cron:
- `DATABASE_URL`
- `ALPACA_PAPER_API_KEY`
- `GEMINI_API_KEY`
- `SERPAPI_API_KEY`
- `AUTOPILOT_MODE=on`
- **TODAS las variables de `coolify/.env.example`**

## 📋 Verificación:
- [ ] Dockerfile tiene `CMD ["tail", "-f", "/dev/null"]`
- [ ] CRON jobs configurados en Coolify (horarios correctos)
- [ ] Variables de entorno cargadas en Coolify
- [ ] Logs directory creado: `/app/logs`

## ⚠️ NO HACER:
- ❌ NO poner el script principal en CMD del Dockerfile
- ❌ NO usar ENTRYPOINT que ejecute código automáticamente
- ❌ NO dejar que el contenedor se ejecute continuamente

## ✅ HACER:
- ✅ Contenedor "sleep" esperando cron jobs
- ✅ CRON jobs ejecutan el script en horarios específicos
- ✅ Verificar logs después de cada ejecución programada