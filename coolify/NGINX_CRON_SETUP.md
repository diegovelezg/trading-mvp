# 🚀 Guía de Configuración de Cron Jobs en Coolify (Nginx)

## 📋 Resumen

Esta guía es para despliegues **directos con Nginx** en Coolify (sin Docker).

---

## 🎯 Opción 1: Cron Jobs Nativos de Coolify (RECOMENDADO)

### Ventajas:
- ✅ Integración directa con Coolify
- ✅ Logs visibles en la interfaz de Coolify
- ✅ Fácil de configurar y modificar
- ✅ Reinicio automático si falla

### Pasos:

1. **Accede a tu aplicación en Coolify**
2. **Ve a "Advanced Settings" → "Cron Jobs"**
3. **Agrega estos 2 cron jobs:**

```bash
# Pre-Market (07:30 AM Lima | 12:30 UTC)
30 12 * * 1-5 cd /var/www/html/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_pre.log 2>&1

# Power Hour (14:00 PM Lima | 19:00 UTC)
0 19 * * 1-5 cd /var/www/html/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_power.log 2>&1
```

### ⚠️ Ajusta las rutas según tu configuración:
- `/var/www/html/trading-mvp` → Tu ruta real del proyecto
- `.venv/bin/python` → O usa `/usr/bin/python3` si no usas venv

---

## 🖥️ Opción 2: Crontab del Servidor VPS

### Ventajas:
- ✅ Control total desde el servidor
- ✅ Independiente de Coolify
- ✅ Logs del sistema disponibles

### Pasos:

1. **SSH a tu servidor**
2. **Ejecuta el script de configuración:**

```bash
cd /ruta/a/tu/proyecto/trading-mvp
chmod +x coolify/setup_crons_nginx.sh
./coolify/setup_crons_nginx.sh
```

O **configura manualmente:**

```bash
# Editar crontab
crontab -e

# Agregar estas líneas:
# Trading MVP - Pre-Market (07:30 AM Lima | 12:30 UTC)
30 12 * * 1-5 cd /ruta/a/tu/proyecto && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_pre.log 2>&1

# Trading MVP - Power Hour (14:00 PM Lima | 19:00 UTC)
0 19 * * 1-5 cd /ruta/a/tu/proyecto && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones >> logs/investment_desk_power.log 2>&1
```

---

## 🔍 Verificación

### Ver logs de ejecución:

```bash
# Logs Pre-Market
tail -f logs/investment_desk_pre.log

# Logs Power Hour
tail -f logs/investment_desk_power.log

# Logs generales del sistema
sudo tail -f /var/log/syslog | grep CRON
```

### Ver crontab activo:

```bash
crontab -l
```

### Test manual:

```bash
cd /ruta/a/tu/proyecto
AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones
```

---

## ⚠️ Troubleshooting

### El cron no se ejecuta:

1. **Verifica la ruta del proyecto:**
   ```bash
   pwd  # Debe mostrar la ruta correcta
   ls ejecutar_mesa_inversiones.py  # Debe existir
   ```

2. **Verifica permisos:**
   ```bash
   chmod +x ejecutar_mesa_inversiones.py
   ```

3. **Verifica Python:**
   ```bash
   which python3  # O la ruta a tu venv
   .venv/bin/python --version  # Si usas venv
   ```

4. **Revisa logs del sistema:**
   ```bash
   sudo tail -f /var/log/syslog | grep CRON
   ```

### Errores de variables de entorno:

1. **Verifica que .yaml exista:**
   ```bash
   ls -la .env  # Debe existir y tener tus API keys
   ```

2. **Verifica AUTOPILOT_MODE:**
   ```bash
   grep AUTOPILOT_MODE .env  # Debe decir AUTOPILOT_MODE=on
   ```

### El script se ejecuta pero no hace trades:

1. **Verifica Risk Management:**
   ```bash
   grep MIN_CONFIDENCE_SCORE .env  # Debe ser 0.75 o similar
   grep MAX_POSITION_SIZE_PCT .env  # Debe ser 0.10 o similar
   ```

2. **Verifica conexión a Alpaca:**
   ```bash
   grep ALPACA_PAPER_API_KEY .env  # Debe tener tu key
   ```

---

## 📊 Monitoreo

### Ver última ejecución:

```bash
python scripts/fetch_latest_execution_data.py
```

### Ver decisiones recientes:

```bash
python scripts/manage_decisions.py --list-recent
```

### Ver logs principales:

```bash
tail -f investment_desk.log
```

---

## 🛡️ Seguridad

- ✅ **NUNCA** commits `.env` a Git
- ✅ Usa `AUTOPILOT_MODE=off` para testing
- ✅ Verifica Risk Management antes de activar autopilot
- ✅ Monitorea logs regularmente

---

## 🎯 Resumen Rápido

| Opción | Dificultad | Control | Integración Coolify |
|--------|------------|---------|-------------------|
| **Cron Nativos** | ⭐ Fácil | ★★ Medio | ✅ Perfecta |
| **Crontab VPS** | ⭐⭐ Medio | ⭐⭐⭐ Alto | ❌ Ninguna |

**Recomendación**: Usa **Cron Nativos de Coolify** para máxima integración.