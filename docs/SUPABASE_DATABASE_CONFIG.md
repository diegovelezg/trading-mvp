# 🔧 CONFIGURACIÓN DE BASE DE DATOS SUPABASE

## 📋 Instrucciones para obtener la URL de conexión de Supabase

### **Opción 1: Desde el Dashboard de Supabase**

1. Ir a https://app.supabase.com
2. Seleccionar tu proyecto
3. Ir a **Settings** → **Database**
4. Copiar **Connection string** → **URI**
5. Debe ser algo como:
   ```
   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

### **Opción 2: Usar la URL actual (si ya es Supabase)**

Si el `DATABASE_URL` actual `YOUR_DATABASE_HOST:6544` YA es Supabase (probablemente una instancia dedicada), entonces ya está todo bien.

## 🎯 Acción Requerida

Añade a tu archivo `.env`:

```bash
# Si YOUR_DATABASE_HOST:6544 NO es Supabase, añade la URL real de Supabase:
SUPABASE_DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@[HOST]:6543/postgres

# Si YOUR_DATABASE_HOST:6544 YA es Supabase, entonces añade solo un alias:
SUPABASE_DATABASE_URL=postgresql://postgres.dev_tenant:YOUR_DATABASE_PASSWORD@YOUR_DATABASE_HOST:6544/postgres
```

## ✅ Verificación

Una vez añadido, ejecuta:
```bash
python -c "from trading_mvp.core.db_manager import init_db; init_db()"
```

Si ves "PostgreSQL connection verified", está todo correcto.
