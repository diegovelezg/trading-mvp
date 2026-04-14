"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { normalizeTicker } from "@/lib/ticker-utils";
import { getDefaultWatchlistId } from "@/lib/config";
import {
  Radar,
  Trash2,
  Search,
  Calendar,
  Info,
  Clock,
  Target,
  Quote,
  CheckCircle2,
  ChevronRight,
  ChevronDown,
  Sparkles,
  Plus,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from "lucide-react";
import { format } from "date-fns";

type Exploration = {
  id: number;
  timestamp: string;
  prompt: string;
  criteria: string;
  tickers: string[];
  ticker_details?: Array<{
    ticker: string;
    name: string;
    sector: string;
    description_es: string;
  }>;
  reasoning?: string;
};

type ActiveItem = {
  ticker: string;
  company_name: string;
  reason: string;
  added_at: string;
  watchlistId: number;
  currentPrice?: number;
  change28d?: number;
  volume?: number;
  // DNA fields
  assetType?: string;
  coreDrivers?: string[];
  bullishCatalysts?: string[];
  bearishCatalysts?: string[];
};

type TickerQuantData = {
  ticker: string;
  currentPrice: number;
  change14d: number;
  change28d: number;
  volume: number;
  marketCap?: number;
};

export default function WatchlistPage() {
  const [activeItems, setActiveItems] = useState<ActiveItem[]>([]);
  const [explorations, setExplorations] = useState<Exploration[]>([]);
  const [tickerQuantData, setTickerQuantData] = useState<Map<string, TickerQuantData>>(new Map());
  const [loadingTickerData, setLoadingTickerData] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'active' | 'history'>('active');
  const [expandedExplorations, setExpandedExplorations] = useState<Set<number>>(new Set());
  const [addingTickers, setAddingTickers] = useState<Set<string>>(new Set());
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'ticker' | 'price' | 'change28d' | 'volume' | 'added_at'>('ticker');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [wlRes, expRes] = await Promise.all([
        fetch("/api/watchlists"),
        fetch("/api/explorations")
      ]);
      const wlData = await wlRes.json();
      const expData = await expRes.json();

      // Extract data from wrapped response
      const watchlistsData = wlData?.data || (Array.isArray(wlData) ? wlData : []);

      // Flatten all items from all watchlists for "Managed" view
      const allActive = watchlistsData.flatMap(wl =>
        (wl.items || [])
          .filter((i: any) => i.ticker) // Filter out items without ticker
          .map((i: any) => ({ ...i, watchlistId: wl.id }))
      );

      setActiveItems(allActive);
      setExplorations(Array.isArray(expData?.data) ? expData.data : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchTickerQuantData = async (ticker: string) => {
    if (tickerQuantData.has(ticker) || loadingTickerData.has(ticker)) {
      return; // Already fetched or loading
    }

    setLoadingTickerData(prev => new Set(prev).add(ticker));

    try {
      const res = await fetch(`/api/ticker-quote?ticker=${ticker}`);
      if (res.ok) {
        const data = await res.json();
        setTickerQuantData(prev => new Map(prev).set(ticker, data));
      }
    } catch (e) {
      console.error(`Failed to fetch quant data for ${ticker}:`, e);
    } finally {
      setLoadingTickerData(prev => {
        const newSet = new Set(prev);
        newSet.delete(ticker);
        return newSet;
      });
    }
  };

  const fetchExplorationTickersData = async (exploration: Exploration) => {
    const tickers = exploration.tickers || [];
    const tickersToFetch = tickers.filter(t => !tickerQuantData.has(t) && !loadingTickerData.has(t));

    // Fetch in parallel with limit
    const batchSize = 5;
    for (let i = 0; i < tickersToFetch.length; i += batchSize) {
      const batch = tickersToFetch.slice(i, i + batchSize);
      await Promise.all(batch.map(t => fetchTickerQuantData(t)));
    }
  };

  const removeTicker = async (watchlistId: number, ticker: string) => {
    if (!confirm(`¿Eliminar ${ticker} del seguimiento ACTIVO?`)) return;
    try {
      const res = await fetch(`/api/watchlists/items?watchlistId=${watchlistId}&ticker=${ticker}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setActiveItems(prev => prev.filter(i => !(i.ticker === ticker && i.watchlistId === watchlistId)));
        showNotification('success', `${ticker} eliminado de la watchlist`);
      }
    } catch (e) {
      console.error(e);
      showNotification('error', `Falló al eliminar ${ticker}`);
    }
  };

  // Filter and sort items
  const filteredAndSortedItems = activeItems
    .filter(item =>
      (item.ticker?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
      (item.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) || false)
    )
    .sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'ticker':
          comparison = (a.ticker || '').localeCompare(b.ticker || '');
          break;
        case 'price':
          comparison = (a.currentPrice || 0) - (b.currentPrice || 0);
          break;
        case 'change28d':
          comparison = (a.change28d || 0) - (b.change28d || 0);
          break;
        case 'volume':
          comparison = (a.volume || 0) - (b.volume || 0);
          break;
        case 'added_at':
          comparison = new Date(a.added_at || 0).getTime() - new Date(b.added_at || 0).getTime();
          break;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const toggleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const addToWatchlist = async (ticker: string, companyName: string, reason: string) => {
    // Check if already in watchlist
    const exists = activeItems.some(item => item.ticker === ticker);
    if (exists) {
      showNotification('error', `${ticker} ya está en la watchlist`);
      return;
    }

    setAddingTickers(prev => new Set(prev).add(ticker));
    try {
      const res = await fetch('/api/watchlists/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          watchlist_id: getDefaultWatchlistId(),
          ticker: normalizeTicker(ticker),
          company_name: companyName,
          reason: reason
        })
      });

      if (res.ok) {
        const newItem = await res.json();
        setActiveItems(prev => [...prev, {
          ticker: newItem.ticker,
          company_name: newItem.company_name || companyName,
          reason: newItem.reason || reason,
          added_at: newItem.added_at || new Date().toISOString(),
          watchlistId: getDefaultWatchlistId()
        }]);
        showNotification('success', `${ticker} añadido a la watchlist`);
      } else {
        const error = await res.json();
        showNotification('error', error.error || `Falló al añadir ${ticker}`);
      }
    } catch (e) {
      console.error(e);
      showNotification('error', `Falló al añadir ${ticker}`);
    } finally {
      setAddingTickers(prev => {
        const newSet = new Set(prev);
        newSet.delete(ticker);
        return newSet;
      });
    }
  };

  const toggleExploration = async (id: number) => {
    const isExpanding = !expandedExplorations.has(id);

    setExpandedExplorations(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });

    // Fetch quant data when expanding
    if (isExpanding) {
      const exploration = explorations.find(e => e.id === id);
      if (exploration) {
        await fetchExplorationTickersData(exploration);
      }
    }
  };

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  const isTickerInWatchlist = (ticker: string) => {
    return activeItems.some(item => item.ticker === ticker);
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <div className="p-10 text-zinc-500 font-mono animate-pulse">_SYNCING_STRATEGY_RADAR...</div>;

  const truncatePrompt = (prompt: string, maxLength: number = 80) => {
    if (prompt.length <= maxLength) return prompt;
    return prompt.substring(0, maxLength) + '...';
  };

  return (
    <TooltipProvider>
      <main className="p-6 md:p-10 max-w-screen-2xl mx-auto space-y-10">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-in slide-in-from-top-2 ${
          notification.type === 'success' ? 'bg-green-950/90 border border-green-800 text-green-300' : 'bg-red-950/90 border border-red-800 text-red-300'
        }`}>
          {notification.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          <span className="text-sm font-medium">{notification.message}</span>
        </div>
      )}
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-zinc-900 pb-10">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter flex items-center gap-3">
            <Radar className="text-blue-500 w-8 h-8" />
            RADAR_DE_ESTRATEGIA
          </h1>
          <p className="text-zinc-500 font-mono text-xs mt-2 uppercase tracking-[0.2em]">
            Gestión de Descubrimiento Autónomo y Seguimiento Activo
          </p>
        </div>

        <div className="flex bg-zinc-900/50 p-1 rounded-lg border border-zinc-800">
          <button
            onClick={() => setActiveTab('active')}
            className={`px-4 py-2 text-xs font-mono uppercase rounded-md transition-all ${activeTab === 'active' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            Watchlist Gestionada ({filteredAndSortedItems.length}{searchTerm && ` / ${activeItems.length}`})
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 text-xs font-mono uppercase rounded-md transition-all ${activeTab === 'history' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            Logs del Explorer ({explorations.length})
          </button>
        </div>
      </div>

      {activeTab === 'active' ? (
        <section className="space-y-6 animate-in fade-in duration-500">
          <div className="flex items-center gap-2 text-zinc-400 mb-2">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <h2 className="text-sm font-mono uppercase tracking-widest">Activos Activos bajo Supervisión</h2>
          </div>

          {/* Search and Sort Controls */}
          <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <input
                type="text"
                placeholder="Buscar ticker o empresa..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-sm text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-700 transition-colors"
              />
            </div>

            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => toggleSort('ticker')}
                className={`px-3 py-2 text-xs font-mono rounded-lg border transition-all flex items-center gap-1.5 ${
                  sortBy === 'ticker'
                    ? 'bg-blue-950/30 border-blue-800 text-blue-400'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-400'
                }`}
              >
                Ticker
                {sortBy === 'ticker' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
                {sortBy !== 'ticker' && <ArrowUpDown className="w-3 h-3 opacity-50" />}
              </button>

              <button
                onClick={() => toggleSort('price')}
                className={`px-3 py-2 text-xs font-mono rounded-lg border transition-all flex items-center gap-1.5 ${
                  sortBy === 'price'
                    ? 'bg-blue-950/30 border-blue-800 text-blue-400'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-400'
                }`}
              >
                Precio
                {sortBy === 'price' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
                {sortBy !== 'price' && <ArrowUpDown className="w-3 h-3 opacity-50" />}
              </button>

              <button
                onClick={() => toggleSort('change28d')}
                className={`px-3 py-2 text-xs font-mono rounded-lg border transition-all flex items-center gap-1.5 ${
                  sortBy === 'change28d'
                    ? 'bg-blue-950/30 border-blue-800 text-blue-400'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-400'
                }`}
              >
                Cambio 28d
                {sortBy === 'change28d' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
                {sortBy !== 'change28d' && <ArrowUpDown className="w-3 h-3 opacity-50" />}
              </button>

              <button
                onClick={() => toggleSort('volume')}
                className={`px-3 py-2 text-xs font-mono rounded-lg border transition-all flex items-center gap-1.5 ${
                  sortBy === 'volume'
                    ? 'bg-blue-950/30 border-blue-800 text-blue-400'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-400'
                }`}
              >
                Volumen
                {sortBy === 'volume' && (sortOrder === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
                {sortBy !== 'volume' && <ArrowUpDown className="w-3 h-3 opacity-50" />}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredAndSortedItems.length === 0 ? (
              <div className="col-span-full h-40 flex items-center justify-center border border-dashed border-zinc-900 rounded-2xl text-zinc-600 font-mono text-xs">
                {searchTerm ? 'SIN_RESULTADOS_PARA_BUSQUEDA' : 'SIN_TICKERS_ACTIVOS_EN_WATCHLIST'}
              </div>
            ) : (
              filteredAndSortedItems.map((item) => (
                <Card key={`${item.watchlistId}-${item.ticker}`} className="group hover:border-zinc-700 transition-all bg-zinc-950/20 border-zinc-900">
                  <CardHeader className="flex flex-row items-center justify-between py-4 pb-2 space-y-0">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="flex items-end gap-2">
                          <span className="text-2xl font-bold tracking-tighter text-zinc-100">{item.ticker}</span>
                          <span className="text-[10px] text-zinc-500 truncate max-w-[120px] font-mono">{item.company_name}</span>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Seguimiento desde {format(new Date(item.added_at), "MMM d, HH:mm")}</p>
                      </TooltipContent>
                    </Tooltip>
                    <button
                      onClick={() => removeTicker(item.watchlistId, item.ticker)}
                      className="p-2 text-zinc-700 hover:text-red-500 hover:bg-red-950/20 rounded-lg transition-all"
                      title="Eliminar del seguimiento"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </CardHeader>
                  <CardContent className="pt-2">
                    {/* Asset DNA Description */}
                    <div className="text-[11px] text-zinc-400 leading-relaxed line-clamp-2 min-h-[32px] border-l border-zinc-800 pl-3">
                      {item.reason && !item.reason.match(/^(Added from exploration|Añadido desde exploración)/) ? (
                        <span className="italic">{item.reason}</span>
                      ) : item.coreDrivers && item.coreDrivers.length > 0 ? (
                        <span>
                          <span className="text-blue-400 not-italic font-semibold">Core Drivers:</span>{' '}
                          {item.coreDrivers.slice(0, 2).join(', ')}
                          {item.coreDrivers.length > 2 && '...'}
                        </span>
                      ) : (
                        <span className="text-zinc-500 italic">
                          {item.assetType || 'Activo en seguimiento'}
                        </span>
                      )}
                    </div>

                    {/* DNA Info */}
                    {item.assetType && (
                      <div className="mt-3 space-y-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-[8px] px-2 py-0 border-blue-900/50 text-blue-400 bg-blue-950/10">
                            🧬 {item.assetType}
                          </Badge>
                        </div>

                        {/* Core Drivers */}
                        {item.coreDrivers && item.coreDrivers.length > 0 && (
                          <div className="space-y-1">
                            <p className="text-[8px] font-mono text-zinc-600 uppercase">Core Drivers</p>
                            <div className="flex flex-wrap gap-1">
                              {item.coreDrivers.slice(0, 3).map((driver, i) => (
                                <span key={i} className="text-[9px] px-1.5 py-0.5 bg-zinc-900 border border-zinc-800 text-zinc-400 rounded">
                                  {driver}
                                </span>
                              ))}
                              {item.coreDrivers.length > 3 && (
                                <span className="text-[9px] px-1.5 py-0.5 text-zinc-600">
                                  +{item.coreDrivers.length - 3}
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Live Alpaca Data */}
                    {(item.currentPrice || item.change28d !== undefined) && (
                      <div className="mt-3 pt-3 border-t border-zinc-900/50 grid grid-cols-3 gap-2">
                        {item.currentPrice && (
                          <div>
                            <div className="text-[8px] font-mono text-zinc-600 uppercase">Precio</div>
                            <div className="text-sm font-bold text-zinc-300">${item.currentPrice?.toFixed(2)}</div>
                          </div>
                        )}
                        {item.change28d !== undefined && item.change28d !== null && (
                          <div>
                            <div className="text-[8px] font-mono text-zinc-600 uppercase">28d</div>
                            <div className={`text-sm font-bold flex items-center gap-1 ${item.change28d >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {item.change28d >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                              {item.change28d >= 0 ? '+' : ''}{item.change28d?.toFixed(1)}%
                            </div>
                          </div>
                        )}
                        {item.volume && (
                          <div>
                            <div className="text-[8px] font-mono text-zinc-600 uppercase">Vol</div>
                            <div className="text-sm font-bold text-zinc-300">{(item.volume / 1000000).toFixed(1)}M</div>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </section>
      ) : (
        <section className="space-y-4 animate-in slide-in-from-bottom-4 duration-500">
          {explorations.length === 0 ? (
            <div className="h-40 flex items-center justify-center border border-dashed border-zinc-900 rounded-2xl text-zinc-600 font-mono text-xs">
              SIN_LOGS_DE_EXPLORACION
            </div>
          ) : (
            explorations.map((exp) => {
              const isExpanded = expandedExplorations.has(exp.id);
              const uniqueTickers = Array.isArray(exp.tickers) ? Array.from(new Set(exp.tickers as string[])) : [];
              const tickerCount = uniqueTickers.length;

              return (
                <div key={exp.id} className="border border-zinc-900 rounded-xl overflow-hidden bg-zinc-950/20">
                  {/* Collapsed Header - Always Visible */}
                  <div
                    onClick={() => toggleExploration(exp.id)}
                    className="p-4 cursor-pointer hover:bg-zinc-900/30 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        <div className="flex items-center gap-2 text-zinc-500">
                          <Calendar className="w-3.5 h-3.5" />
                          <span className="text-[10px] font-mono">
                            {format(new Date(exp.timestamp), "MMM d, yyyy • HH:mm")}
                          </span>
                        </div>
                        <div className="h-4 w-px bg-zinc-800" />
                        <p className="text-sm text-zinc-300 flex-1 truncate">
                          &quot;{truncatePrompt(exp.prompt)}&quot;
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className="text-[10px] font-mono border-zinc-800 px-2 py-0.5">
                          {tickerCount} {tickerCount === 1 ? 'ticker' : 'tickers'}
                        </Badge>
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4 text-zinc-500" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-zinc-500" />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Content - Lazy Loaded */}
                  {isExpanded && (
                    <div className="border-t border-zinc-900 p-6 space-y-6 animate-in fade-in duration-300">
                      {/* USER PROMPT QUOTE */}
                      <div className="bg-zinc-950/50 p-6 rounded-2xl border border-zinc-900 relative overflow-hidden group">
                        <Quote className="absolute -right-4 -top-4 w-24 h-24 text-zinc-900/40 rotate-12 group-hover:text-blue-900/20 transition-colors" />
                        <div className="relative z-10">
                          <p className="text-[10px] font-mono text-blue-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                            <Sparkles className="w-3 h-3" /> Solicitud de Búsqueda del Usuario
                          </p>
                          <p className="text-lg font-medium text-zinc-300 tracking-tight leading-relaxed italic">
                            &quot;{exp.prompt}&quot;
                          </p>
                        </div>
                      </div>

                      {/* CRITERIA SUMMARY */}
                      <div className="flex items-start gap-3 text-sm text-zinc-500 bg-zinc-900/20 p-4 rounded-xl border border-zinc-900/50">
                        <Search className="w-4 h-4 mt-0.5 text-zinc-600 shrink-0" />
                        <p>
                          <span className="text-zinc-400 font-mono text-[10px] uppercase mr-2 font-bold">
                            Lógica del Explorer:
                          </span>
                          {exp.criteria}
                        </p>
                      </div>

                      {/* SUGGESTED TICKERS WITH ADD TO WATCHLIST */}
                      <div className="space-y-3">
                        <p className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                          <Target className="w-3 h-3" />
                          Tickers Descubiertos
                        </p>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                          {uniqueTickers.map((t: string) => {
                            const inWatchlist = isTickerInWatchlist(t);
                            const addingTicker = addingTickers.has(t);
                            const quantData = tickerQuantData.get(t);
                            const tickerDetail = exp.ticker_details?.find(d => d.ticker === t);
                            const isLoadingData = loadingTickerData.has(t);

                            return (
                              <div
                                key={`${exp.id}-${t}`}
                                className={`bg-zinc-900/40 border p-4 rounded-lg transition-all ${
                                  inWatchlist ? 'border-green-900/30' : 'border-zinc-800/50'
                                }`}
                              >
                                <div className="space-y-3">
                                  {/* Header: Ticker + Add Button */}
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                      <span className="text-xl font-bold text-zinc-200">{t}</span>
                                      {inWatchlist && (
                                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                                      )}
                                      {isLoadingData && (
                                        <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                                      )}
                                    </div>
                                    {!inWatchlist && (
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          addToWatchlist(t, tickerDetail?.name || '', tickerDetail?.description_es || 'Ticker añadido desde exploración');
                                        }}
                                        disabled={addingTicker}
                                        className="px-3 py-1.5 text-[10px] font-mono uppercase bg-blue-900/20 hover:bg-blue-900/40 text-blue-400 border border-blue-900/50 rounded transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                                      >
                                        {addingTicker ? (
                                          <span className="animate-pulse">Añadiendo...</span>
                                        ) : (
                                          <>
                                            <Plus className="w-3 h-3" />
                                            Añadir
                                          </>
                                        )}
                                      </button>
                                    )}
                                  </div>

                                  {/* Company Info */}
                                  {tickerDetail && (
                                    <div className="space-y-2">
                                      <p className="text-sm font-semibold text-zinc-300">{tickerDetail.name}</p>
                                      <div className="flex items-center gap-2">
                                        <Badge variant="outline" className="text-[8px] px-2 py-0 border-zinc-700 text-zinc-400">
                                          {tickerDetail.sector}
                                        </Badge>
                                      </div>
                                      <p className="text-[11px] text-zinc-400 leading-relaxed">{tickerDetail.description_es}</p>
                                    </div>
                                  )}

                                  {/* Quant Data from Alpaca */}
                                  {quantData && (
                                    <div className="grid grid-cols-4 gap-2 pt-2 border-t border-zinc-800/50">
                                      <div>
                                        <div className="text-[8px] font-mono text-zinc-600 uppercase">Precio</div>
                                        <div className="text-sm font-bold text-zinc-300">
                                          ${quantData.currentPrice.toFixed(2)}
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-[8px] font-mono text-zinc-600 uppercase">14d</div>
                                        <div className={`text-sm font-bold flex items-center gap-1 ${quantData.change14d >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                          {quantData.change14d >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                          {quantData.change14d >= 0 ? '+' : ''}{quantData.change14d.toFixed(1)}%
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-[8px] font-mono text-zinc-600 uppercase">28d</div>
                                        <div className={`text-sm font-bold flex items-center gap-1 ${quantData.change28d >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                          {quantData.change28d >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                          {quantData.change28d >= 0 ? '+' : ''}{quantData.change28d.toFixed(1)}%
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-[8px] font-mono text-zinc-600 uppercase">Volumen</div>
                                        <div className="text-sm font-bold text-zinc-300">
                                          {(quantData.volume / 1000000).toFixed(1)}M
                                        </div>
                                      </div>
                                    </div>
                                  )}

                                  {/* Relation to search criteria */}
                                  <div className="bg-blue-950/10 border border-blue-900/20 p-2 rounded">
                                    <p className="text-[9px] text-blue-400 font-mono uppercase mb-1">Relación con criterio</p>
                                    <p className="text-[10px] text-zinc-400 italic">
                                      {tickerDetail?.description_es || 'Componente del sector solicitado en la búsqueda temática.'}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* AGENT RATIONALE */}
                      {exp.reasoning && (
                        <div className="bg-blue-950/10 border border-blue-900/20 p-4 rounded-xl">
                          <p className="text-[10px] font-mono text-zinc-500 uppercase mb-2">Raciocinio del Descubrimiento</p>
                          <p className="text-xs text-zinc-400 leading-relaxed italic">
                            {exp.reasoning}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </section>
      )}
      </main>
    </TooltipProvider>
  );
}
