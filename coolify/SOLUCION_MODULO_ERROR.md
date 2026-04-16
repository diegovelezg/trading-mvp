# ✅ SOLUCIÓN COMPLETA: Error "No module named trading-mvp"

## 🎯 PROBLEMA RESUELTO

El error `/opt/venv/bin/python: No module named trading-mvp` ocurrió porque el módulo no estaba instalado como paquete Python ni en el PYTHONPATH.

## 🚀 CAMBIOS REALIZADOS:

### 1. **Creado `setup.py`** ✅
Define el paquete `trading_mvp` para instalación.

### 2. **Actualizado `Dockerfile`** ✅
Ahora instala el paquete en modo editable:
```dockerfile
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -e .
```

### 3. **Mejorado `ejecutar_mesa_inversiones.py`** ✅
Mejor manejo de paths para desarrollo y producción.

### 4. **Actualizado `requirements.txt`** ✅
Agregada dependencia faltante: `python-dateutil>=2.8.0`

### 5. **Creado `test_imports.py`** ✅
Script de test para verificar que todo funciona.

### 6. **Creado `coolify/COOLIFY_TROUBLESHOOTING.md`** ✅
Guía de troubleshooting completa.

## ⚡ CONFIGURACIÓN EN COOLIFY (ACTUALIZADA):

### **TAB GENERAL** (Nixpacks):
```yaml
Name: trading-mvp-python
Build Pack: Nixpacks
⚠️ DESMARCAR "Is it a static site?"

Install Command: python3 -m venv .venv && .venv/bin/pip install --upgrade pip
Build Command: pip install -e .
Start Command: tail -f /dev/null

Ports Exposes: [VACÍO]
```

### **TAB ENVIRONMENT VARIABLES**:
```bash
# CRÍTICO - Agregar esta PRIMERA:
PYTHONPATH=/app:/app/scripts

# + todas las demás variables de coolify/.env.example
```

### **TAB SCHEDULED TASKS**:
```bash
# Task 1 - Pre-Market:
Command: python ejecutar_mesa_inversiones
Cron: 30 12 * * 1-5

# Task 2 - Power Hour:
Command: python ejecutar_mesa_inversiones
Cron: 0 19 * * 1-5
```

## 📊 TESTEO EN COOLIFY:

Después del deploy, en **Terminal** del contenedor:

```bash
# 1. Verificar imports
python test_imports.py

# 2. Test manual del script
python ejecutar_mesa_inversiones

# 3. Verificar PYTHONPATH
echo $PYTHONPATH
# Debe mostrar: /app:/app/scripts
```

## 🎯 PRÓXIMOS PASOS:

1. **Hacer commit** de los cambios:
   ```bash
   git add setup.py Dockerfile test_imports.py requirements.txt ejecutar_mesa_inversiones.py coolify/
   git commit -m "fix: configuración para Coolify - solución error módulo trading-mvp"
   git push
   ```

2. **En Coolify**: Click **"Deploy"**

3. **Verificar logs** para confirmar que el build es exitoso

4. **Testear** el scheduled task manualmente

## ✅ EXPECTED RESULT:

- ✅ Build sin errores
- ✅ Contenedor en estado "Running"
- ✅ Scheduled tasks se ejecutan según el cron
- ✅ Logs se generan en `/app/logs/`
- ✅ AutoPilot ejecuta órdenes si se cumplen las condiciones

## 📞 SI SIGUE SIN FUNCIONAR:

Revisar:
1. Logs del build en Coolify
2. Que `setup.py` esté en la raíz del repo
3. Que `PYTHONPATH` incluya `/app:/app/scripts`
4. Ejecutar `python test_imports.py` en el contenedor

---

**ESTE ERROR DEBE ESTAR RESUELTO** con los cambios implementados. 🚀