import os
import logging
import sys

# Agregar ruta al sistema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading_mvp.core.db_manager import get_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_news_ttl():
    """Configura un job de pg_cron en Supabase para limpiar noticias de más de 90 días."""
    logger.info("🔧 Configurando TTL (90 días) para noticias en Supabase...")
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Habilitar extensión (normalmente ya habilitada en Supabase, pero por si acaso)
            # En Supabase, la mayoría de extensiones van al esquema "extensions"
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_cron SCHEMA extensions;")
            
            # 2. Crear función segura para borrar
            logger.info("📜 Creando función 'delete_old_news_ttl()'")
            cur.execute("""
                CREATE OR REPLACE FUNCTION delete_old_news_ttl()
                RETURNS void
                LANGUAGE plpgsql
                SECURITY DEFINER
                AS $$
                BEGIN
                    -- Borrar noticias más antiguas de 90 días basándose en published_at o collected_at
                    -- Nota: Los embeddings en news_embeddings se borrarán en cascada gracias al FK (ON DELETE CASCADE)
                    DELETE FROM geo_macro_news
                    WHERE COALESCE(published_at, collected_at) < CURRENT_TIMESTAMP - INTERVAL '90 days';
                END;
                $$;
            """)
            
            # 3. Remover el schedule si ya existe para evitar errores
            logger.info("⏱️ Eliminando schedules previos (si existen)...")
            try:
                cur.execute("SELECT cron.unschedule('purge_old_news_job');")
            except Exception as e:
                # Si no existe el job, no pasa nada
                conn.commit()  # Resetear transacción tras error menor
                
            # 4. Programar el cron job
            # Se ejecutará a la medianoche (0 0 * * *) todos los días
            logger.info("⏰ Programando nuevo pg_cron job para que corra cada medianoche...")
            cur.execute("""
                SELECT cron.schedule(
                    'purge_old_news_job',  -- Nombre del job
                    '0 0 * * *',           -- Expresión Cron: Medianoche UTC todos los días
                    'SELECT delete_old_news_ttl();' -- Comando a ejecutar
                );
            """)
            
        conn.commit()
        logger.info("✅ ¡TTL Configurado con éxito! Las noticias antiguas se borrarán automáticamente.")
    except Exception as e:
        logger.error(f"❌ Error al configurar TTL: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    setup_news_ttl()