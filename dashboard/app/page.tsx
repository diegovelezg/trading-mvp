"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  TrendingUp, 
  BarChart3, 
  History, 
  BrainCircuit,
  Filter,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Zap,
  Wallet,
  Briefcase,
  Clock,
  Search,
  MessageSquare,
  TrendingDown,
  Target,
  AlertTriangle
} from "lucide-react";
import { format } from "date-fns";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState(format(new Date(), "yyyy-MM-dd"));

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [statsRes, activityRes, portfolioRes] = await Promise.all([
          fetch("/api/stats"),
          fetch(`/api/activity?date=${dateFilter}`),
          fetch("/api/portfolio")
        ]);
        
        const statsData = await statsRes.json();
        const activityData = await activityRes.json();
        const portfolioData = await portfolioRes.json();
        
        setStats(statsData?.error ? null : statsData);
        setActivities(Array.isArray(activityData) ? activityData : []);
        setPortfolio(portfolioData?.error ? null : portfolioData);
      } catch (e) {
        console.error("Fetch error:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [dateFilter]);

  if (loading && !portfolio) return <div className="p-10 text-zinc-500 font-mono animate-pulse">_SYNCING_EVIDENCE_LOGS...</div>;

  return (
    <main className="p-6 md:p-10 max-w-6xl mx-auto space-y-10">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter flex items-center gap-2">
            <Activity className="text-zinc-400" />
            AGN_OS_DESK
          </h1>
          <p className="text-zinc-500 font-mono text-sm mt-1 uppercase tracking-widest">
            Evidence-Based Autonomous Trading
          </p>
        </div>
        
        <div className="flex items-center gap-4 bg-zinc-950 p-2 rounded-lg border border-zinc-900">
          <Filter className="w-4 h-4 text-zinc-500" />
          <input 
            type="date" 
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-sm font-mono text-zinc-300"
          />
        </div>
      </div>

      {/* PORTFOLIO HEALTH */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Equity" value={`$${portfolio?.equity?.toLocaleString() || 0}`} icon={<Wallet className="text-blue-500" />} />
        <KPICard title="Buying Power" value={`$${portfolio?.buying_power?.toLocaleString() || 0}`} icon={<Zap className="text-yellow-500" />} />
        <KPICard title="Bot Success" value={stats?.sharpeRatio || 0} icon={<TrendingUp className="text-green-500" />} label="Sharpe" />
        <KPICard title="Total Decisions" value={stats?.totalDecisions || 0} icon={<BrainCircuit className="text-purple-500" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT: ALPACA REAL-TIME */}
        <div className="lg:col-span-4 space-y-8">
          <div className="space-y-4">
            <h2 className="text-xs font-bold flex items-center gap-2 uppercase tracking-[0.2em] text-zinc-500">
              <Briefcase className="w-3 h-3" />
              Live Positions
            </h2>
            <Card className="bg-zinc-950/20 border-zinc-900 overflow-hidden">
              <CardContent className="p-0">
                {portfolio?.positions?.length === 0 ? (
                  <div className="p-8 text-center text-zinc-700 font-mono text-[10px]">NO_OPEN_POSITIONS</div>
                ) : (
                  <div className="divide-y divide-zinc-900">
                    {portfolio?.positions?.map((pos: any) => (
                      <div key={pos.symbol} className="p-4 flex justify-between items-center hover:bg-zinc-900/30 transition-colors">
                        <div>
                          <span className="font-bold text-zinc-200">{pos.symbol}</span>
                          <p className="text-[10px] text-zinc-500 font-mono">{pos.qty} Shrs @ ${parseFloat(pos.avg_entry_price).toFixed(2)}</p>
                        </div>
                        <div className="text-right">
                          <p className={`font-mono text-xs font-bold ${parseFloat(pos.unrealized_pl) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {parseFloat(pos.unrealized_pl) >= 0 ? '+' : ''}{parseFloat(pos.unrealized_pl).toFixed(2)}
                          </p>
                          <p className="text-[9px] text-zinc-600">{(parseFloat(pos.unrealized_plpc) * 100).toFixed(2)}%</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <h2 className="text-xs font-bold flex items-center gap-2 uppercase tracking-[0.2em] text-zinc-500">
              <Clock className="w-3 h-3 text-yellow-600" />
              Pending Orders
            </h2>
            <Card className="bg-zinc-950/20 border-zinc-900 overflow-hidden">
              <CardContent className="p-0">
                {portfolio?.orders?.length === 0 ? (
                  <div className="p-8 text-center text-zinc-700 font-mono text-[10px]">NO_PENDING_ORDERS</div>
                ) : (
                  <div className="divide-y divide-zinc-900">
                    {portfolio?.orders?.map((ord: any) => (
                      <div key={ord.id} className="p-4 flex justify-between items-center bg-yellow-950/5">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-zinc-200">{ord.symbol}</span>
                            <Badge variant="outline" className="text-[8px] py-0 border-yellow-900/50 text-yellow-600">{ord.status}</Badge>
                          </div>
                          <p className="text-[10px] text-zinc-500 font-mono uppercase">{ord.side} {ord.qty} units</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-xs text-zinc-400">Target</p>
                          <p className="text-[10px] text-zinc-500">${parseFloat(ord.limit_price || ord.filled_avg_price || 0).toFixed(2)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* RIGHT: THE DECISION FEED WITH EVIDENCE */}
        <div className="lg:col-span-8 space-y-6">
          <h2 className="text-lg font-bold flex items-center gap-2 uppercase tracking-tighter">
            <History className="w-4 h-4 text-zinc-500" />
            THE_DECISION_FEED
          </h2>
          
          {activities.length === 0 ? (
            <div className="h-60 flex flex-col items-center justify-center border border-dashed border-zinc-900 rounded-2xl text-zinc-600">
              <p className="font-mono text-xs uppercase opacity-50">NO_DATA_FOR_{dateFilter}</p>
            </div>
          ) : (
            <div className="space-y-6">
              {activities.map((act) => (
                <DecisionCard key={act.decision_id} activity={act} />
              ))}
            </div>
          )}
        </div>

      </div>
    </main>
  );
}

function KPICard({ title, value, icon, label }: any) {
  return (
    <Card className="bg-zinc-950/50 border-zinc-900">
      <CardContent className="p-6 flex items-center justify-between">
        <div>
          <p className="text-xs font-mono uppercase text-zinc-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-zinc-100">{value}</p>
          {label && <p className="text-[9px] text-zinc-600 font-mono mt-1 uppercase">{label}</p>}
        </div>
        <div className="bg-zinc-900 p-2 rounded-lg">{icon}</div>
      </CardContent>
    </Card>
  );
}

function DecisionCard({ activity }: any) {
  const [expanded, setExpanded] = useState(false);
  const isBuy = activity.action_taken === 'BUY' || activity.desk_action === 'BUY';
  const analysis = activity.analysis || {};
  
  // Extract agent evidence
  const bullCase = analysis.bull_case || {};
  const bearCase = analysis.bear_case || {};
  const riskAnalysis = analysis.risk_analysis || {};
  const quant = analysis.quant_stats || analysis.quant_metrics || {};

  return (
    <Card className="hover:border-zinc-700 transition-all bg-zinc-950/40">
      <div className="cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <CardHeader className="flex flex-row items-center justify-between py-6">
          <div className="flex items-center gap-4">
            <Badge variant={isBuy ? "success" : "secondary"} className="px-3 py-1">
              {activity.desk_action || 'WAIT'}
            </Badge>
            <div>
              <span className="text-2xl font-bold tracking-tighter text-zinc-100">{activity.ticker}</span>
              <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest mt-1">
                {activity.recommendation} • {activity.status}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="text-xs text-zinc-500 font-mono uppercase">Position Size</p>
              <p className="text-sm font-bold text-zinc-300">
                ${Number(activity.position_size || 0).toLocaleString()}
              </p>
            </div>
            {expanded ? <ChevronUp className="w-5 h-5 text-zinc-500" /> : <ChevronDown className="w-5 h-5 text-zinc-500" />}
          </div>
        </CardHeader>
        
        <CardContent className="pb-6">
          <div className="text-sm text-zinc-300 leading-relaxed mb-6 italic border-l-2 border-zinc-800 pl-4 py-1">
            "{activity.rationale || activity.decision_notes}"
          </div>
          
          <div className="flex flex-wrap gap-4">
            <QuantItem label="RSI" value={quant.rsi_14} />
            <QuantItem label="Beta" value={quant.beta_spy} />
            <QuantItem label="Sentiment" value={activity.sentiment_score ? `${(activity.sentiment_score * 100).toFixed(1)}%` : '--'} />
            <QuantItem label="Confidence" value={analysis.avg_confidence ? `${(analysis.avg_confidence * 100).toFixed(0)}%` : '--'} />
          </div>
        </CardContent>
      </div>

      {expanded && (
        <CardContent className="pt-8 border-t border-zinc-900 bg-zinc-950/60">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            
            {/* BULL EVIDENCE */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-green-500">
                <TrendingUp className="w-4 h-4" />
                <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Bull Evidence</h3>
              </div>
              <ul className="space-y-2">
                {bullCase.arguments?.map((arg: string, i: number) => (
                  <li key={i} className="text-[11px] text-zinc-400 flex gap-2">
                    <span className="text-green-900 font-bold">•</span> {arg}
                  </li>
                ))}
              </ul>
              {bullCase.deep_analysis && (
                <div className="mt-4 p-3 bg-green-950/5 rounded border border-green-900/20">
                  <p className="text-[9px] text-green-700 font-mono uppercase mb-1 font-bold">Analyst Monologue</p>
                  <p className="text-[10px] text-zinc-400 leading-relaxed italic">{bullCase.deep_analysis}</p>
                </div>
              )}
            </div>

            {/* BEAR EVIDENCE */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-red-500">
                <TrendingDown className="w-4 h-4" />
                <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Bear Risks</h3>
              </div>
              <ul className="space-y-2">
                {bearCase.arguments?.map((arg: string, i: number) => (
                  <li key={i} className="text-[11px] text-zinc-400 flex gap-2">
                    <span className="text-red-900 font-bold">•</span> {arg}
                  </li>
                ))}
              </ul>
              {bearCase.deep_analysis && (
                <div className="mt-4 p-3 bg-red-950/5 rounded border border-red-900/20">
                  <p className="text-[9px] text-red-700 font-mono uppercase mb-1 font-bold">Skeptic Monologue</p>
                  <p className="text-[10px] text-zinc-400 leading-relaxed italic">{bearCase.deep_analysis}</p>
                </div>
              )}
            </div>

            {/* RISK MANAGEMENT */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-yellow-500">
                <ShieldCheck className="w-4 h-4" />
                <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Risk Strategy</h3>
              </div>
              <div className="bg-zinc-900/30 p-4 rounded-xl border border-zinc-900 space-y-3">
                <div className="flex justify-between text-xs">
                  <span className="text-zinc-500 font-mono">STOP_LOSS</span>
                  <span className="text-red-500 font-bold">{riskAnalysis.stop_loss?.percentage * 100 || 5}%</span>
                </div>
                <p className="text-[10px] text-zinc-500 italic leading-snug">
                  Defense: {riskAnalysis.stop_loss?.technical_defense || "Standard variance protection."}
                </p>
              </div>
              {riskAnalysis.deep_analysis && (
                <div className="p-3 bg-yellow-950/5 rounded border border-yellow-900/20">
                  <p className="text-[9px] text-yellow-700 font-mono uppercase mb-1 font-bold">Risk Ratiocination</p>
                  <p className="text-[10px] text-zinc-400 leading-relaxed">{riskAnalysis.deep_analysis}</p>
                </div>
              )}
            </div>

            {/* CIO FINAL RATIONALE DETAILS */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-blue-500">
                <BrainCircuit className="w-4 h-4" />
                <h3 className="text-xs font-bold uppercase tracking-widest font-mono">CIO Strategy</h3>
              </div>
              <div className="text-[11px] text-zinc-400 leading-relaxed space-y-2">
                <p><b className="text-zinc-300">Net Sentiment:</b> {analysis.positive_ratio > analysis.negative_ratio ? 'Positive Bias' : 'Negative Bias'}</p>
                <p><b className="text-zinc-300">Model:</b> GLM-5.1 Strategic Brain</p>
                <p><b className="text-zinc-300">Verdict:</b> {activity.decision_notes}</p>
              </div>
            </div>

          </div>
        </CardContent>
      )}
    </Card>
  );
}

function QuantItem({ label, value }: any) {
  const displayValue = typeof value === 'number' ? value.toFixed(2) : value;
  return (
    <div className="bg-zinc-900/50 px-3 py-2 rounded border border-zinc-900 flex flex-col min-w-[80px]">
      <span className="text-[9px] font-mono text-zinc-600 uppercase mb-1">{label}</span>
      <span className="text-xs font-bold text-zinc-300">{displayValue || '--'}</span>
    </div>
  );
}
