"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
  Sparkles
} from "lucide-react";
import { format } from "date-fns";

export default function WatchlistPage() {
  const [activeItems, setActiveItems] = useState<any[]>([]);
  const [explorations, setExplorations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'active' | 'history'>('active');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [wlRes, expRes] = await Promise.all([
        fetch("/api/watchlists"),
        fetch("/api/explorations")
      ]);
      const wlData = await wlRes.json();
      const expData = await expRes.json();
      
      // Flatten all items from all watchlists for "Managed" view
      const allActive = (Array.isArray(wlData) ? wlData : []).flatMap(wl => 
        wl.items.map((i: any) => ({ ...i, watchlistId: wl.id }))
      );
      
      setActiveItems(allActive);
      setExplorations(Array.isArray(expData) ? expData : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const removeTicker = async (watchlistId: number, ticker: string) => {
    if (!confirm(`Remove ${ticker} from ACTIVE tracking?`)) return;
    try {
      const res = await fetch(`/api/watchlists/items?watchlistId=${watchlistId}&ticker=${ticker}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setActiveItems(prev => prev.filter(i => !(i.ticker === ticker && i.watchlistId === watchlistId)));
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <div className="p-10 text-zinc-500 font-mono animate-pulse">_SYNCING_STRATEGY_RADAR...</div>;

  return (
    <main className="p-6 md:p-10 max-w-6xl mx-auto space-y-10">
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-zinc-900 pb-10">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter flex items-center gap-3">
            <Radar className="text-blue-500 w-8 h-8" />
            STRATEGY_RADAR
          </h1>
          <p className="text-zinc-500 font-mono text-xs mt-2 uppercase tracking-[0.2em]">
            Managing Autonomous Discovery & Active Tracking
          </p>
        </div>

        <div className="flex bg-zinc-900/50 p-1 rounded-lg border border-zinc-800">
          <button 
            onClick={() => setActiveTab('active')}
            className={`px-4 py-2 text-xs font-mono uppercase rounded-md transition-all ${activeTab === 'active' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            Managed Watchlist ({activeItems.length})
          </button>
          <button 
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 text-xs font-mono uppercase rounded-md transition-all ${activeTab === 'history' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            Explorer Logs ({explorations.length})
          </button>
        </div>
      </div>

      {activeTab === 'active' ? (
        <section className="space-y-6 animate-in fade-in duration-500">
          <div className="flex items-center gap-2 text-zinc-400 mb-2">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <h2 className="text-sm font-mono uppercase tracking-widest">Active Assets under Supervision</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeItems.length === 0 ? (
              <div className="col-span-full h-40 flex items-center justify-center border border-dashed border-zinc-900 rounded-2xl text-zinc-600 font-mono text-xs">
                NO_ACTIVE_TICKERS_IN_WATCHLIST
              </div>
            ) : (
              activeItems.map((item) => (
                <Card key={`${item.watchlistId}-${item.ticker}`} className="group hover:border-zinc-700 transition-all bg-zinc-950/20 border-zinc-900">
                  <CardHeader className="flex flex-row items-center justify-between py-4 pb-2 space-y-0">
                    <div>
                      <span className="text-2xl font-bold tracking-tighter text-zinc-100">{item.ticker}</span>
                      <p className="text-[10px] text-zinc-500 truncate max-w-[160px] font-mono mt-0.5">{item.company_name}</p>
                    </div>
                    <button 
                      onClick={() => removeTicker(item.watchlistId, item.ticker)}
                      className="p-2 text-zinc-700 hover:text-red-500 hover:bg-red-950/20 rounded-lg transition-all"
                      title="Remove from tracking"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </CardHeader>
                  <CardContent className="pt-2">
                    <div className="text-[11px] text-zinc-400 leading-relaxed line-clamp-2 min-h-[32px] italic border-l border-zinc-800 pl-3">
                      {item.reason}
                    </div>
                    <div className="mt-4 pt-3 border-t border-zinc-900/50 flex justify-between items-center">
                       <span className="text-[9px] font-mono text-zinc-600 uppercase">Tracked since</span>
                       <span className="text-[9px] font-mono text-zinc-500">{format(new Date(item.added_at), "MMM d, HH:mm")}</span>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </section>
      ) : (
        <section className="space-y-10 animate-in slide-in-from-bottom-4 duration-500">
          {explorations.map((exp) => (
            <div key={exp.id} className="relative pl-8 border-l border-zinc-900 space-y-6">
              <div className="absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full bg-blue-900 border border-black" />
              
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-3 text-zinc-500">
                  <Clock className="w-4 h-4" />
                  <span className="text-xs font-mono">{format(new Date(exp.timestamp), "MMMM d, yyyy • HH:mm:ss")}</span>
                </div>
                <Badge variant="outline" className="w-fit text-[10px] font-mono border-zinc-800 px-3">
                  ID: {exp.id}
                </Badge>
              </div>

              <div className="space-y-4">
                {/* USER PROMPT QUOTE */}
                <div className="bg-zinc-950/50 p-6 rounded-2xl border border-zinc-900 relative overflow-hidden group">
                  <Quote className="absolute -right-4 -top-4 w-24 h-24 text-zinc-900/40 rotate-12 group-hover:text-blue-900/20 transition-colors" />
                  <div className="relative z-10">
                    <p className="text-[10px] font-mono text-blue-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                      <Sparkles className="w-3 h-3" /> User Search Request
                    </p>
                    <p className="text-lg font-medium text-zinc-300 tracking-tight leading-relaxed italic">
                      "{exp.prompt}"
                    </p>
                  </div>
                </div>

                {/* CRITERIA SUMMARY */}
                <div className="flex items-start gap-3 text-sm text-zinc-500 bg-zinc-900/20 p-4 rounded-xl border border-zinc-900/50">
                  <Search className="w-4 h-4 mt-0.5 text-zinc-600 shrink-0" />
                  <p><span className="text-zinc-400 font-mono text-[10px] uppercase mr-2 font-bold">Explorer Logic:</span> {exp.criteria}</p>
                </div>

                {/* SUGGESTED TICKERS */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {Array.isArray(exp.tickers) && exp.tickers.map((t: string) => (
                    <div key={t} className="bg-zinc-900/40 border border-zinc-800/50 p-3 rounded-lg flex items-center justify-center group hover:bg-zinc-800 transition-colors">
                      <span className="font-bold text-zinc-300 group-hover:text-white transition-colors">{t}</span>
                    </div>
                  ))}
                </div>

                {/* AGENT RATIONALE */}
                <div className="bg-blue-950/10 border border-blue-900/20 p-4 rounded-xl">
                   <p className="text-[10px] font-mono text-zinc-500 uppercase mb-2">Discovery Rationale</p>
                   <p className="text-xs text-zinc-400 leading-relaxed italic">
                     {exp.reasoning || "Agent identified these assets as primary candidates for the requested investment theme."}
                   </p>
                </div>
              </div>
            </div>
          ))}
        </section>
      )}
    </main>
  );
}
