-- Añadir columna ticker_details a la tabla explorations
-- Este campo guardará el JSON completo con metadatos de cada ticker

ALTER TABLE explorations
ADD COLUMN IF NOT EXISTS ticker_details JSONB DEFAULT '[]'::jsonb;

-- Crear índice para búsquedas eficientes
CREATE INDEX IF NOT EXISTS idx_explorations_ticker_details ON explorations USING GIN (ticker_details);

-- Comentario para documentación
COMMENT ON COLUMN explorations.ticker_details IS 'JSON completo con metadatos de tickers descubiertos: [{ticker, name, sector, description_es}]';
