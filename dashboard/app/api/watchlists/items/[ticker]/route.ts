import { NextRequest } from 'next/server';
import { supabase } from '@/lib/supabase';
import { withErrorHandler, NotFoundError, BadRequestError } from '@/lib/api-error-handler';
import { successResponse } from '@/lib/api-response';
import { updateWatchlistItemSchema } from '@/lib/schemas/watchlist';
import { normalizeTicker } from '@/lib/ticker-utils';

/**
 * PUT /api/watchlists/items/[ticker]
 *
 * Actualizar un item de watchlist
 */
export const PUT = withErrorHandler(
  async (req: NextRequest, { params }: { params: Promise<{ ticker: string }> }) => {
    const { ticker } = await params;
    const body = await req.json();
    const { watchlist_id, company_name, reason } = body;

    // Validar
    if (!watchlist_id) {
      throw new BadRequestError('watchlist_id is required');
    }

    // Normalizar ticker (aunque el schema ya lo hace, esto es explícito)
    const normalizedTicker = normalizeTicker(ticker);

    const validatedData = updateWatchlistItemSchema.parse({
      watchlist_id: parseInt(watchlist_id.toString()),
      ticker: normalizedTicker,
      company_name: company_name || null,
      reason: reason || null
    });

    const { data: item, error } = await supabase
      .from('watchlist_items')
      .update({
        company_name: validatedData.company_name,
        reason: validatedData.reason
      })
      .eq('watchlist_id', validatedData.watchlist_id)
      .eq('ticker', validatedData.ticker)
      .select()
      .single();

    if (error) throw error;

    if (!item) {
      throw new NotFoundError('Item not found');
    }

    return successResponse(item);
  }
);
