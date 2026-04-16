# 🔧 Solución al Error "No module named trading-mvp"

## 🐛 Problema:
```
/opt/venv/bin/python: No module named trading-mvp
```

## ✅ CAUSA RAÍZ:
El módulo `trading_mvp` no está instalado como paquete Python ni está en el PYTHONPATH.

## 🚀 SOLUCIÓN (3 opciones, elegir 1):

### **Opción 1: Instalar como paquete (RECOMENDADO)** ✅

Esta es la solución MÁS ROBUSTA. Instala `trading_mvp` como paquete Python.

#### En Coolify UI - General Tab:

**Si usas Nixpacks:**
```yaml
Build Command: pip install -e .
```

**Si usas Dockerfile:**
El `Dockerfile` ya está actualizado con:
```dockerfile
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -e .
```

### **Opción 2: Ajustar PYTHONPATH**

Agrega PYTHONPATH a las Environment Variables:

#### En Coolify UI - Environment Variables Tab:
```bash
PYTHONPATH=/app:/app/scripts
```

### **Opción 3: Usar python -m (módulo)**

Ejecuta como módulo en lugar de script:

#### En Coolify UI - Scheduled Tasks Tab:
```bash
# Cambiar de:
.venv/bin/python ejecutar_mesa_inversiones

# A:
.venv/bin/python -m ejecutar_mesa_inversiones
```

## 🎯 RECOMENDACIÓN FINAL:

**Usar Opción 1 + Opción 2** (máxima robustez):

1. **Instalar como paquete** (Opción 1)
2. **Set PYTHONPATH** (Opción 2)

### Configuración completa en Coolify:

**General Tab:**
```yaml
Build Pack: Nixpacks
Build Command: pip install -e .
Start Command: tail -f /dev/null
```

**Environment Variables Tab:**
```bash
# Agregar esta variable:
PYTHONPATH=/app:/app/scripts

# + todas las demás variables de .env.example
```

**Scheduled Tasks Tab:**
```bash
Command: python ejecutar_mesa_inversiones
# NOTA: Sin .venv/bin/ si el paquete está instalado
```

## 📊 VERIFICACIÓN:

Después del deploy, en el terminal del contenedor:

```bash
# Verificar que trading_mvp está instalado
python -c "import trading_mvp; print('✅ trading_mvp importado correctamente')"

# Verificar PYTHONPATH
echo $PYTHONPATH
# Debería mostrar: /app:/app/scripts

# Verificar el script principal
python ejecutar_mesa_inversiones --help
```

## 🚨 Si SIGUE sin funcionar:

1. **Revisar logs del build** en Coolify
2. **Verificar que setup.py existe** en la raíz
3. **Verificar que requirements.txt** tiene todas las dependencias
4. **Test manual en el contenedor**:
   ```bash
   pip install -e .
   python ejecutar_mesa_inversiones
   ```

## 📝 Archivos modificados:

1. **`setup.py`** - Creado (define el paquete)
2. **`Dockerfile`** - Actualizado (instala el paquete)
3. **`ejecutar_mesa_inversiones.py`** - Actualizado (mejor manejo de paths)

## 🎯 PRÓXIMOS PASOS:

1. Hacer commit de estos cambios
2. En Coolify, click "Deploy"
3. Verificar que el build sea exitoso
4. Testear el scheduled task manualmente