import { NextRequest } from 'next/server';
import { supabase } from '@/lib/supabase';
import { withErrorHandler, BadRequestError, NotFoundError } from '@/lib/api-error-handler';
import { successResponse } from '@/lib/api-response';
import { addWatchlistItemSchema } from '@/lib/schemas/watchlist';
import { normalizeTicker } from '@/lib/ticker-utils';

/**
 * POST /api/watchlists/items
 *
 * Añadir un ticker a una watchlist
 */
export const POST = withErrorHandler(async (req: NextRequest) => {
  const body = await req.json();

  // Validar con Zod
  const validatedData = addWatchlistItemSchema.parse(body);

  const { data: item, error } = await supabase
    .from('watchlist_items')
    .insert({
      watchlist_id: validatedData.watchlist_id,
      ticker: validatedData.ticker,
      company_name: validatedData.company_name || null,
      reason: validatedData.reason || null
    })
    .select()
    .single();

  if (error) {
    // Error de duplicado
    if (error.message?.includes('duplicate') || error.code === '23505') {
      throw new BadRequestError('Ticker already exists in this watchlist');
    }
    throw error;
  }

  return successResponse(item, undefined, 201);
});

/**
 * DELETE /api/watchlists/items
 *
 * Eliminar un ticker de una watchlist
 */
export const DELETE = withErrorHandler(async (req: NextRequest) => {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get('ticker');
  const watchlistId = searchParams.get('watchlistId');

  // Validar params manualmente (no hay schema para query params en Zod fácilmente)
  if (!ticker || !watchlistId) {
    throw new BadRequestError('Missing ticker or watchlistId');
  }

  const watchlistIdNum = parseInt(watchlistId, 10);
  if (isNaN(watchlistIdNum)) {
    throw new BadRequestError('Invalid watchlistId');
  }

  // Normalizar ticker
  const normalizedTicker = normalizeTicker(ticker);

  const { error } = await supabase
    .from('watchlist_items')
    .delete()
    .eq('watchlist_id', watchlistIdNum)
    .eq('ticker', normalizedTicker);

  if (error) throw error;

  return successResponse({ success: true, ticker: normalizedTicker, watchlistId: watchlistIdNum });
});
