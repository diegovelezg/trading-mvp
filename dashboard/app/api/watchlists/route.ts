import { NextRequest } from 'next/server';
import { supabase } from '@/lib/supabase';
import { withErrorHandler } from '@/lib/api-error-handler';
import { successResponse } from '@/lib/api-response';
import { createWatchlistSchema } from '@/lib/schemas/watchlist';

/**
 * POST /api/watchlists
 *
 * Crear una nueva watchlist
 */
export const POST = withErrorHandler(async (req: NextRequest) => {
  const body = await req.json();

  // Validar con Zod
  const validatedData = createWatchlistSchema.parse(body);

  const { data: watchlist, error } = await supabase
    .from('watchlists')
    .insert({
      name: validatedData.name,
      description: validatedData.description || null,
      criteria_prompt: validatedData.criteria_prompt || null,
      criteria_summary: validatedData.criteria_summary || null,
      status: 'active'
    })
    .select()
    .single();

  if (error) throw error;

  return successResponse(watchlist, undefined, 201);
});

/**
 * GET /api/watchlists
 *
 * Obtener todas las watchlists activas con sus items y datos en vivo
 */
export const GET = withErrorHandler(async (req: NextRequest) => {
  // Fetch active watchlists with item count
  const { data: watchlists, error } = await supabase
    .from('watchlists')
    .select(`
      id,
      name,
      description,
      criteria_summary,
      created_at,
      watchlist_items(count)
    `)
    .eq('status', 'active')
    .order('created_at', { ascending: false });

  if (error) throw error;

  // Fetch items for each watchlist in parallel with live Alpaca data
  const watchlistsWithItems = await Promise.all(
    watchlists.map(async (wl: any) => {
      const { data: items, error: itemsError } = await supabase
        .from('watchlist_items')
        .select('ticker, company_name, reason, added_at')
        .eq('watchlist_id', wl.id)
        .order('added_at', { ascending: false });

      if (itemsError) throw itemsError;

      // Get DNA data and live ticker data from Alpaca
      const tickers = items.map(item => item.ticker);
      const { getBatchTickerData } = await import('@/lib/alpaca');
      const [liveData, dnaData] = await Promise.all([
        getBatchTickerData(tickers),
        // Fetch DNA from asset_dna table
        supabase
          .from('asset_dna')
          .select('ticker, asset_type, core_drivers, bullish_catalysts, bearish_catalysts')
          .in('ticker', tickers)
      ]);

      // Create DNA lookup map
      const dnaMap = new Map((dnaData.data || []).map(dna => [dna.ticker, dna]));

      // Merge static data with live data and DNA
      const itemsWithLive = items.map(item => {
        const live = liveData.find(d => d.ticker === item.ticker);
        const dna = dnaMap.get(item.ticker);
        return {
          ...item,
          currentPrice: live?.currentPrice,
          change14d: live?.change14d,
          change28d: live?.change28d,
          volume: live?.volume,
          lastUpdated: live?.lastUpdated,
          // DNA info
          assetType: dna?.asset_type,
          coreDrivers: dna?.core_drivers,
          bullishCatalysts: dna?.bullish_catalysts,
          bearishCatalysts: dna?.bearish_catalysts,
        };
      });

      // Simplify ticker_count from the count join
      const ticker_count = wl.watchlist_items?.[0]?.count || 0;

      return { ...wl, ticker_count, items: itemsWithLive };
    })
  );

  return successResponse(watchlistsWithItems, {
    count: watchlistsWithItems.length,
    resource: 'watchlists'
  });
});
