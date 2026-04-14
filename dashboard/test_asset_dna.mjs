import { createClient } from '@supabase/supabase-js';
import { config } from 'dotenv';
import { resolve } from 'path';

// Cargar .env desde el directorio padre
config({ path: resolve(process.cwd(), '../.env') });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

async function testAssetDna() {
  console.log('🧪 Probando acceso a asset_dna desde Supabase client...');
  
  const { data, error } = await supabase
    .from('asset_dna')
    .select('ticker, asset_type, core_drivers')
    .in('ticker', ['NVDA', 'AAPL', 'TSLA'])
    .limit(3);
  
  if (error) {
    console.log('❌ Error:', error.message);
    console.log('   Details:', error);
    process.exit(1);
  } else {
    console.log('✅ Datos recuperados exitosamente!');
    console.log('📊 Muestra:', JSON.stringify(data, null, 2));
  }
}

testAssetDna();
