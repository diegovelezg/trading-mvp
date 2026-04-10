import { supabase } from '@/lib/supabase';
import { withErrorHandler } from '@/lib/api-error-handler';
import { successResponse } from '@/lib/api-response';

/**
 * GET /api/explorations
 *
 * Obtener todas las exploraciones recientes
 */
export const GET = withErrorHandler(async () => {
  const { data: explorations, error } = await supabase
    .from('explorations')
    .select('id, prompt, criteria, tickers, ticker_details, reasoning, created_at')
    .order('created_at', { ascending: false });

  if (error) throw error;

  // Parse tickers from JSONB (Supabase automatically parses it)
  const parsedExplorations = (explorations || []).map(exp => ({
    id: exp.id,
    prompt: exp.prompt,
    criteria: exp.criteria,
    reasoning: exp.reasoning,
    timestamp: exp.created_at, // Map created_at to timestamp for backward compatibility
    tickers: Array.isArray(exp.tickers) ? exp.tickers : [],
    ticker_details: exp.ticker_details || []
  }));

  return successResponse(parsedExplorations, {
    count: parsedExplorations.length,
    resource: 'explorations'
  });
});
