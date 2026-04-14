-- Crear tabla asset_dna para almacenar el perfil de ADN de cada activo
CREATE TABLE IF NOT EXISTS asset_dna (
    ticker VARCHAR(10) PRIMARY KEY,
    asset_type VARCHAR(255) NOT NULL,
    core_drivers TEXT[] NOT NULL,
    bullish_catalysts TEXT[] NOT NULL,
    bearish_catalysts TEXT[] NOT NULL,
    geopolitical_sensitivity FLOAT DEFAULT 0.5,
    interest_rate_sensitivity FLOAT DEFAULT 0.5,
    embedding VECTOR(1536),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice para búsquedas rápidas por ticker
CREATE INDEX IF NOT EXISTS idx_asset_dna_ticker ON asset_dna(ticker);

-- Índice para búsquedas semánticas por similitud de embeddings
CREATE INDEX IF NOT EXISTS idx_asset_dna_embedding ON asset_dna USING ivfflat (embedding vector_cosine_ops);

-- Comentarios para documentación
COMMENT ON TABLE asset_dna IS 'Single Source of Truth (SSOT) para el perfil de ADN de cada activo';
COMMENT ON COLUMN asset_dna.ticker IS 'Símbolo del ticker (ej: AAPL, NVDA)';
COMMENT ON COLUMN asset_dna.asset_type IS 'Tipo de activo (ej: Hyper-Growth Semi/AI, Long-Duration Bond ETF)';
COMMENT ON COLUMN asset_dna.core_drivers IS 'Lista de factores principales que mueven el precio';
COMMENT ON COLUMN asset_dna.bullish_catalysts IS 'Situaciones que AUMENTAN el precio según su naturaleza';
COMMENT ON COLUMN asset_dna.bearish_catalysts IS 'Situaciones que DISMINUYEN el precio según su naturaleza';
COMMENT ON COLUMN asset_dna.geopolitical_sensitivity IS 'Sensibilidad a eventos geopolíticos (0.0 a 1.0)';
COMMENT ON COLUMN asset_dna.interest_rate_sensitivity IS 'Sensibilidad a tipos de interés (0.0 a 1.0)';
COMMENT ON COLUMN asset_dna.embedding IS 'Vector embedding para búsquedas semánticas';

-- Habilitar RLS (Row Level Security) para control de acceso granular
ALTER TABLE asset_dna ENABLE ROW LEVEL SECURITY;

-- Política para permitir lectura pública (solo SELECT) a través de la API de Supabase
CREATE POLICY "Allow public read access" ON asset_dna
    FOR SELECT
    USING (true);

-- Política para permitir inserciones desde el backend con service_role
-- (Nota: Esto requiere autenticación con service_role key, no con anon key)
CREATE POLICY "Allow service role insert" ON asset_dna
    FOR INSERT
    WITH CHECK (true);

-- Política para permitir actualizaciones desde el backend con service_role
CREATE POLICY "Allow service role update" ON asset_dna
    FOR UPDATE
    USING (true)
    WITH CHECK (true);
