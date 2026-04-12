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
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Shield,
  Zap,
  Wallet,
  Briefcase,
  Clock,
  MessageSquare,
  TrendingDown,
  Target,
  AlertTriangle
} from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer } from "recharts";
import { format } from "date-fns";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [statsRes, activityRes, portfolioRes] = await Promise.all([
          fetch("/api/stats"),
          fetch("/api/activity"),
          fetch("/api/portfolio")
        ]);

        const statsData = await statsRes.json();
        const activityData = await activityRes.json();
        const portfolioData = await portfolioRes.json();

        setStats(statsData?.error ? null : statsData?.data);
        setActivities(Array.isArray(activityData) ? activityData : []);
        setPortfolio(portfolioData);
      } catch (e) {
        console.error("Fetch error:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading && !portfolio) return <div className="p-10 text-zinc-500 font-mono animate-pulse">_SYNCING_EVIDENCE_LOGS...</div>;

  return (
    <main className="p-6 md:p-10 max-w-screen-2xl mx-auto space-y-10">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter flex items-center gap-2">
            <Activity className="text-zinc-400" />
            AGN_OS_DESK
          </h1>
          <p className="text-zinc-500 font-mono text-sm mt-1 uppercase tracking-widest">
            Trading Autónomo Basado en Evidencia
          </p>
        </div>
      </div>

      {/* PORTFOLIO HEALTH */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard 
          title="Equity Total" 
          value={`$${portfolio?.equity?.toLocaleString() || 0}`} 
          icon={<Wallet className="text-blue-500" />} 
          label={`${stats?.returnPct >= 0 ? '+' : ''}${stats?.returnPct || 0}% ($${stats?.totalPL || 0})`} 
        />
        <KPICard 
          title="Profit Factor" 
          value={`${stats?.profitFactor || 0}`} 
          icon={<Zap className={stats?.profitFactor > 1.5 ? "text-green-500" : "text-yellow-500"} />} 
          label={`Max Drawdown: -${stats?.maxDrawdown || 0}%`}
        />
        <KPICard 
          title="Éxito del Bot" 
          value={`${stats?.winRate || 0}%`} 
          icon={<TrendingUp className="text-green-500" />} 
          label={`Sharpe Ratio: ${stats?.sharpeRatio || 0}`} 
        />
        <KPICard 
          title="Decisiones Totales" 
          value={stats?.totalDecisions || 0} 
          icon={<BrainCircuit className="text-purple-500" />} 
          label={`News Processed: ${stats?.newsProcessed || 0}`}
        />
      </div>

      {/* EQUITY CURVE CHART */}
      {stats?.equityHistory && stats.equityHistory.length > 0 && (
        <Card className="bg-zinc-950/20 border-zinc-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 font-mono uppercase tracking-widest flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-500" />
              Equity Curve (1M)
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[250px] w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.equityHistory} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="time" 
                  stroke="#52525b" 
                  fontSize={10} 
                  tickLine={false} 
                  axisLine={false} 
                  minTickGap={30}
                />
                <YAxis 
                  domain={['auto', 'auto']} 
                  stroke="#52525b" 
                  fontSize={10} 
                  tickLine={false} 
                  axisLine={false} 
                  tickFormatter={(val) => `$${val.toLocaleString()}`}
                  width={65}
                />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', fontSize: '12px', fontFamily: 'monospace', borderRadius: '8px' }}
                  itemStyle={{ color: '#e4e4e7' }}
                  formatter={(value: any) => [`$${parseFloat(value).toLocaleString()}`, 'Equity']}
                  labelStyle={{ color: '#a1a1aa', marginBottom: '4px' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="equity" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorEquity)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT: ALPACA REAL-TIME */}
        <div className="lg:col-span-3 space-y-8">
          <div className="space-y-4">
            <h2 className="text-xs font-bold flex items-center gap-2 uppercase tracking-[0.2em] text-zinc-500">
              <Briefcase className="w-3 h-3" />
              Posiciones en Vivo
            </h2>
            <Card className="bg-zinc-950/20 border-zinc-900 overflow-hidden">
              <CardContent className="p-0">
                {portfolio?.positions?.length === 0 ? (
                  <div className="p-8 text-center text-zinc-700 font-mono text-[10px]">SIN_POSICIONES_ABIERTAS</div>
                ) : (
                  <div className="divide-y divide-zinc-900">
                    {portfolio?.positions?.map((pos: any) => (
                      <div key={pos.symbol} className="p-4 flex justify-between items-center hover:bg-zinc-900/30 transition-colors">
                        <div>
                          <span className="font-bold text-zinc-200">{pos.symbol}</span>
                          <p className="text-[10px] text-zinc-500 font-mono">{pos.qty} acciones @ ${parseFloat(pos.avg_entry_price).toFixed(2)}</p>
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
              Órdenes Pendientes
            </h2>
            <Card className="bg-zinc-950/20 border-zinc-900 overflow-hidden">
              <CardContent className="p-0">
                {portfolio?.orders?.length === 0 ? (
                  <div className="p-8 text-center text-zinc-700 font-mono text-[10px]">SIN_ORDENES_PENDIENTES</div>
                ) : (
                  <div className="divide-y divide-zinc-900">
                    {portfolio?.orders?.map((ord: any) => (
                      <div key={ord.id} className="p-4 flex justify-between items-center bg-yellow-950/5">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-zinc-200">{ord.symbol}</span>
                            <Badge variant="outline" className="text-[8px] py-0 border-yellow-900/50 text-yellow-600">{ord.status}</Badge>
                          </div>
                          <p className="text-[10px] text-zinc-500 font-mono uppercase">{ord.side} {ord.qty} unidades</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-xs text-zinc-400">Objetivo</p>
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
        <div className="lg:col-span-9 space-y-6">
          <h2 className="text-lg font-bold flex items-center gap-2 uppercase tracking-tighter">
            <History className="w-4 h-4 text-zinc-500" />
            FEED_DE_DECISIONES
          </h2>

          {activities.length === 0 ? (
            <div className="h-60 flex flex-col items-center justify-center border border-dashed border-zinc-900 rounded-2xl text-zinc-600">
              <p className="font-mono text-xs uppercase opacity-50">SIN_DATOS</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Group activities by desk_run_id */}
              {(() => {
                const groupedByDesk = activities.reduce((acc: any, act: any) => {
                  const deskId = act.desk_run_id || 'no-desk';
                  if (!acc[deskId]) {
                    acc[deskId] = [];
                  }
                  acc[deskId].push(act);
                  return acc;
                }, {});

                // Sort desk runs by most recent activity (first activity in each group is already newest)
                const sortedDeskIds = Object.entries(groupedByDesk)
                  .sort(([, a]: any, [, b]: any) => {
                    const aTime = new Date(a[0].decision_timestamp).getTime();
                    const bTime = new Date(b[0].decision_timestamp).getTime();
                    return bTime - aTime; // Descending order (newest first)
                  })
                  .map(([deskId]) => deskId);

                return sortedDeskIds.map((deskId) => (
                  <DeskRunCard
                    key={deskId}
                    deskRunId={deskId}
                    activities={groupedByDesk[deskId]}
                    alpacaOrders={portfolio?.orders || []}
                  />
                ));
              })()}
            </div>
          )}
        </div>

      </div>
    </main>
  );
}

function DeskRunCard({ deskRunId, activities, alpacaOrders = [] }: any) {
  const [expanded, setExpanded] = useState(true); // Default expanded

  // Extract desk info from first activity
  const firstActivity = activities[0] || {};
  const deskTimestamp = firstActivity.decision_timestamp || firstActivity.created_at;
  const tickerCount = activities.length;

  return (
    <Card className="bg-zinc-950/80 border-zinc-900">
      <div className="cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <CardHeader className="flex flex-row items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <History className="w-5 h-5 text-zinc-400" />
            <div>
              <h3 className="text-sm font-bold text-zinc-100">
                🏛️ MESA DE INVERSIONES #{deskRunId !== 'no-desk' ? deskRunId : 'N/A'}
              </h3>
              <p className="text-[10px] text-zinc-500 font-mono">
                {new Date(deskTimestamp).toLocaleString()} • {tickerCount} tickers analizados
              </p>
            </div>
          </div>
          {expanded ? <ChevronUp className="w-5 h-5 text-zinc-500" /> : <ChevronDown className="w-5 h-5 text-zinc-500" />}
        </CardHeader>

        {expanded && (
          <CardContent className="space-y-3 pb-6">
            {activities
              .sort((a: any, b: any) => new Date(b.decision_timestamp).getTime() - new Date(a.decision_timestamp).getTime())
              .map((activity: any) => (
              <DecisionCard
                key={activity.decision_id || activity.ticker}
                activity={activity}
                alpacaOrders={alpacaOrders}
                isNested={true}
              />
            ))}
          </CardContent>
        )}
      </div>
    </Card>
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

function DecisionCard({ activity, alpacaOrders = [], isNested = false }: any) {
  const [expanded, setExpanded] = useState(false);
  const isBuy = activity.action_taken === 'BUY' || activity.desk_action === 'BUY';
  const analysis = activity.analysis || {};

  // Try to find live status in current Alpaca orders
  const liveOrder = activity.alpaca_order_id ? alpacaOrders.find((o: any) => o.id === activity.alpaca_order_id) : null;
  const currentStatus = liveOrder ? liveOrder.status.toUpperCase() : activity.status;

  // Extract agent evidence
  const bullCase = analysis.bull_case || {};
  const bearCase = analysis.bear_case || {};
  const riskAnalysis = analysis.risk_analysis || {};
  const quant = analysis.quant_stats || analysis.quant_metrics || {};

  // NESTED MODE: Compact header, full content on expand
  if (isNested) {
    return (
      <Card className="bg-zinc-900/40 border border-zinc-900/50 hover:border-zinc-800 transition-all">
        {/* COMPACT HEADER */}
        <div className="cursor-pointer" onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}>
          <div className="flex flex-row items-center justify-between p-3">
            <div className="flex items-center gap-3">
              <Badge variant={isBuy ? "success" : "secondary"} className="px-2 py-0.5 text-[10px]">
                {activity.desk_action || 'WAIT'}
              </Badge>
              <span className="text-lg font-bold text-zinc-100">{activity.ticker}</span>
              <span className="text-[9px] text-zinc-500 font-mono uppercase">
                {activity.recommendation}
              </span>
              {activity.sentiment_score !== null && activity.sentiment_score !== undefined && (
                <span className={`text-[9px] font-bold ${activity.sentiment_score > 0 ? 'text-green-500' : activity.sentiment_score < 0 ? 'text-red-500' : 'text-zinc-500'}`}>
                  {activity.sentiment_score > 0 ? '+' : ''}{(activity.sentiment_score * 100).toFixed(0)}%
                </span>
              )}
            </div>
            {expanded ? <ChevronUp className="w-4 h-4 text-zinc-600" /> : <ChevronDown className="w-4 h-4 text-zinc-600" />}
          </div>
        </div>

        {/* FULL CONTENT ON EXPAND - SAME AS STANDALONE */}
        {expanded && (
          <CardContent className="pb-6 border-t border-zinc-900/50">
            <div className="text-sm text-zinc-300 leading-relaxed mb-6 italic border-l-2 border-zinc-800 pl-4 py-1">
              &quot;{activity.rationale || activity.decision_notes}&quot;
            </div>

            <div className="flex flex-wrap gap-4 mb-6">
              <QuantItem label="RSI" value={quant.rsi_14} />
              <QuantItem label="Beta" value={quant.beta_spy} />
              <QuantItem label="RVOL" value={quant.rvol} />
              <QuantItem label="Corr SPY" value={quant.corr_spy_20d} />
              <QuantItem label="Sentiment" value={(activity.sentiment_score !== null && activity.sentiment_score !== undefined) ? `${(activity.sentiment_score * 100).toFixed(1)}%` : '--'} />
              <QuantItem label="Final Score" value={(activity.confidence_in_decision !== null && activity.confidence_in_decision !== undefined) ? `${(activity.confidence_in_decision * 100).toFixed(0)}%` : '--'} />
            </div>

            {/* DETAILED QUANT GRID */}
            <div className="mb-8 p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-4">
                <div className="flex items-center gap-2 text-zinc-400">
                  <BarChart3 className="w-4 h-4" />
                  <h4 className="text-[11px] font-bold uppercase tracking-[0.2em] font-mono text-zinc-500">Análisis Técnico</h4>
                </div>
                <Badge variant="outline" className="text-[8px] uppercase font-mono border-zinc-800 text-zinc-600">60% Peso Decisión</Badge>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                {/* Structure */}
                <div className="space-y-3">
                  <p className="text-[9px] text-zinc-600 uppercase font-mono font-bold tracking-wider">Estructura de Mercado</p>
                  <div className="text-[11px] text-zinc-400 space-y-2">
                    <p className="flex justify-between"><span>SMA 200</span> <span className="text-zinc-200 font-mono">${quant.sma_200?.toFixed(2)}</span></p>
                    <p className="flex justify-between"><span>SMA 50</span> <span className="text-zinc-200 font-mono">${quant.sma_50?.toFixed(2)}</span></p>
                    <p className="flex justify-between"><span>Dist. Tendencia</span> <span className={`font-mono font-bold ${quant.price_to_sma200_dist > 0 ? 'text-green-500' : 'text-red-500'}`}>{quant.price_to_sma200_dist?.toFixed(1)}%</span></p>
                  </div>
                </div>

                {/* Momentum */}
                <div className="space-y-3">
                  <p className="text-[9px] text-zinc-600 uppercase font-mono font-bold tracking-wider">Momentum</p>
                  <div className="text-[11px] text-zinc-400 space-y-2">
                    <p className="flex justify-between"><span>Línea MACD</span> <span className="text-zinc-200 font-mono">{quant.macd?.line?.toFixed(3)}</span></p>
                    <p className="flex justify-between"><span>Señal</span> <span className="text-zinc-200 font-mono">{quant.macd?.signal?.toFixed(3)}</span></p>
                    <p className="flex justify-between"><span>Histograma</span> <span className={`font-mono font-bold ${quant.macd?.histogram > 0 ? 'text-green-500' : 'text-red-500'}`}>{quant.macd?.histogram?.toFixed(3)}</span></p>
                  </div>
                </div>

                {/* Conviction */}
                <div className="space-y-3">
                  <p className="text-[9px] text-zinc-600 uppercase font-mono font-bold tracking-wider">Convicción</p>
                  <div className="text-[11px] text-zinc-400 space-y-2">
                    <p className="flex justify-between"><span>Tendencia</span> <span className={`font-mono font-bold ${quant.trend === 'BULLISH' ? 'text-green-500' : 'text-red-500'}`}>{quant.trend}</span></p>
                    <p className="flex justify-between"><span>OBV</span> <span className="text-zinc-200 font-mono">{(quant.obv / 1000000).toFixed(1)}M</span></p>
                    <p className="text-[9px] text-zinc-700 italic mt-1">RVOL activo en resumen</p>
                  </div>
                </div>

                {/* Risk */}
                <div className="space-y-3">
                  <p className="text-[9px] text-zinc-600 uppercase font-mono font-bold tracking-wider">Volatilidad</p>
                  <div className="text-[11px] text-zinc-400 space-y-2">
                    <p className="flex justify-between"><span>ATR (14)</span> <span className="text-zinc-200 font-mono">${quant.atr_14?.toFixed(2)}</span></p>
                    <p className="flex justify-between"><span>Vol. Histórica</span> <span className="text-zinc-200 font-mono">{quant.std_dev_20?.toFixed(2)}%</span></p>
                    <p className="flex justify-between"><span>Riesgo/Precio</span> <span className="text-zinc-200 font-mono">{quant.volatility_ratio?.toFixed(2)}%</span></p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">

              {/* BULL EVIDENCE */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-500">
                  <TrendingUp className="w-4 h-4" />
                  <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Evidencia Bullish</h3>
                </div>
                <ul className="space-y-2">
                  {bullCase.arguments && bullCase.arguments.length > 0 ? (
                    bullCase.arguments.map((arg: string, i: number) => (
                      <li key={i} className="text-[11px] text-zinc-400 flex gap-2">
                        <span className="text-green-900 font-bold">•</span> {arg}
                      </li>
                    ))
                  ) : (
                    <li className="text-[11px] text-zinc-600 italic">No se detectaron señales positivas en noticias recientes</li>
                  )}
                </ul>

                {/* EVIDENCE CHAIN: NEWS → ENTITY */}
                {bullCase.evidence_chain && bullCase.evidence_chain.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-[9px] font-mono uppercase text-zinc-600">📰 Noticias Fuente</p>
                    {bullCase.evidence_chain.map((evidence: any, i: number) => (
                      <div key={i} className="bg-zinc-900/50 p-2 rounded border-l-2 border-green-700">
                        <p className="text-[10px] text-zinc-400 font-mono truncate" title={evidence.news_title}>
                          "{evidence.news_title}"
                        </p>
                        <p className="text-[9px] text-zinc-500 mt-1">
                          <span className="text-green-700">→</span> {evidence.entity_name} ({evidence.impact}, {Math.round(evidence.confidence * 100)}% conf)
                          <span className="text-zinc-600 ml-2">[{evidence.news_source}]</span>
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {bullCase.deep_analysis && (
                  <div className="mt-4 p-3 bg-green-950/5 rounded border border-green-900/20">
                    <p className="text-[9px] text-green-700 font-mono uppercase mb-1 font-bold">Monólogo del Analista</p>
                    <p className="text-[10px] text-zinc-400 leading-relaxed italic">{bullCase.deep_analysis}</p>
                  </div>
                )}
              </div>

              {/* BEAR EVIDENCE */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-red-500">
                  <TrendingDown className="w-4 h-4" />
                  <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Riesgos Bearish</h3>
                </div>
                <ul className="space-y-2">
                  {bearCase.arguments?.map((arg: string, i: number) => (
                    <li key={i} className="text-[11px] text-zinc-400 flex gap-2">
                      <span className="text-red-900 font-bold">•</span> {arg}
                    </li>
                  ))}
                </ul>

                {/* EVIDENCE CHAIN: NEWS → ENTITY */}
                {bearCase.evidence_chain && bearCase.evidence_chain.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-[9px] font-mono uppercase text-zinc-600">📰 Noticias Fuente</p>
                    {bearCase.evidence_chain.map((evidence: any, i: number) => (
                      <div key={i} className="bg-zinc-900/50 p-2 rounded border-l-2 border-red-700">
                        <p className="text-[10px] text-zinc-400 font-mono truncate" title={evidence.news_title}>
                          "{evidence.news_title}"
                        </p>
                        <p className="text-[9px] text-zinc-500 mt-1">
                          <span className="text-red-700">→</span> {evidence.entity_name} ({evidence.impact}, {Math.round(evidence.confidence * 100)}% conf)
                          <span className="text-zinc-600 ml-2">[{evidence.news_source}]</span>
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {bearCase.deep_analysis && (
                  <div className="mt-4 p-3 bg-red-950/5 rounded border border-red-900/20">
                    <p className="text-[9px] text-red-700 font-mono uppercase mb-1 font-bold">Monólogo del Escéptico</p>
                    <p className="text-[10px] text-zinc-400 leading-relaxed italic">{bearCase.deep_analysis}</p>
                  </div>
                )}
              </div>

              {/* RISK & EXECUTION PANEL */}
              <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-zinc-900">
                
                {/* RISK STRATEGY */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-yellow-500">
                    <ShieldCheck className="w-4 h-4" />
                    <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Perfil de Riesgo</h3>
                  </div>

                  <div className="bg-zinc-900/30 rounded-2xl border border-zinc-900 overflow-hidden">
                    <div className="p-4 border-b border-zinc-900 flex justify-between items-center bg-yellow-950/5">
                      <span className="text-[10px] font-mono text-zinc-500 uppercase">Red de Seguridad</span>
                      <div className="text-right">
                        <span className="text-xs font-bold text-red-500 font-mono">STOP LOSS @ {riskAnalysis.stop_loss?.percentage * 100 || 5}%</span>
                      </div>
                    </div>
                    <div className="p-4 space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="mt-1 p-1 bg-zinc-900 rounded">
                          <AlertTriangle className="w-3 h-3 text-zinc-600" />
                        </div>
                        <p className="text-[11px] text-zinc-400 leading-relaxed italic">
                          "{riskAnalysis.deep_analysis || riskAnalysis.stop_loss?.technical_defense || "Protección estándar de varianza aplicada basada en la volatilidad del activo."}"
                        </p>
                      </div>
                      <div className="flex gap-2 pt-2">
                        <Badge variant="outline" className="text-[8px] bg-zinc-950 border-zinc-800 text-zinc-500">RSI: {quant.rsi_14?.toFixed(1)}</Badge>
                        <Badge variant="outline" className="text-[8px] bg-zinc-950 border-zinc-800 text-zinc-500">ATR: ${quant.atr_14?.toFixed(2)}</Badge>
                        <Badge variant="outline" className={`text-[8px] bg-zinc-950 border-zinc-800 ${activity.recommendation === 'BUY' ? 'text-green-500' : 'text-yellow-500'}`}>
                          NVL: {activity.recommendation === 'BUY' ? 'AGRESIVO' : 'CAUTELOSO'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>

                {/* ORDER TICKET (EXECUTION) */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-purple-500">
                    <Zap className="w-4 h-4" />
                    <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Ticket de Orden</h3>
                  </div>

                  <div className="bg-purple-950/5 rounded-2xl border border-purple-900/20 p-5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                      <Target className="w-12 h-12 text-purple-500" />
                    </div>

                    <div className="space-y-4 relative z-10">
                      <div className="flex justify-between items-end">
                        <div>
                          <p className="text-[9px] font-mono text-purple-500 uppercase mb-1">Asignación</p>
                          <p className="text-2xl font-black text-zinc-100 font-mono">
                            {activity.position_size ? `$${activity.position_size.toLocaleString()}` : '$0.00'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-[9px] font-mono text-zinc-600 uppercase mb-1">Objetivo de Entrada</p>
                          <p className="text-sm font-bold text-zinc-400 font-mono">
                            {activity.entry_price ? `$${activity.entry_price.toFixed(2)}` : 'MERCADO'}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-purple-900/20">
                        <div>
                          <p className="text-[8px] font-mono text-zinc-600 uppercase mb-1">Referencia del Broker</p>
                          <p className="text-[10px] font-mono text-zinc-400 truncate">
                            {activity.alpaca_order_id || '---'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-[8px] font-mono text-zinc-600 uppercase mb-1">Estado</p>
                          <Badge className={`text-[9px] font-mono font-bold ${
                            currentStatus === 'FILLED' ? 'bg-green-500/10 text-green-500 border-green-500/20' :
                            currentStatus === 'PENDING' || currentStatus === 'NEW' ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                            'bg-zinc-800 text-zinc-500 border-zinc-700'
                          }`}>
                            {currentStatus || 'ESPERA'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* CIO FINAL RATIONALE */}
              <div className="space-y-4 md:col-span-2 pt-6 border-t border-zinc-900">
                <div className="flex items-center gap-2 text-blue-500">
                  <BrainCircuit className="w-4 h-4" />
                  <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Resumen de Inteligencia Estratégica</h3>
                </div>
                <div className="bg-blue-950/5 border border-blue-900/20 rounded-xl p-5">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-6 text-[11px] items-center">
                    <div className="md:col-span-2 space-y-1">
                      <p className="text-zinc-500 font-mono uppercase text-[9px]">Motor de Decisión</p>
                      <p className="text-zinc-300 font-bold">GLM-5.1 Strategic Brain</p>
                    </div>

                    <div className="md:col-span-7 space-y-1 border-l border-blue-900/20 pl-6">
                      <p className="text-zinc-500 font-mono uppercase text-[9px]">Razón de Ejecución y Contexto</p>
                      <p className="text-[11px] text-zinc-300 leading-relaxed font-mono italic">
                        "{activity.decision_notes || 'No se proporcionó contexto adicional de decisión por el modelo.'}"
                      </p>
                    </div>

                    <div className="md:col-span-3 space-y-1 border-l border-blue-900/20 pl-6 text-right">
                      <p className="text-zinc-500 font-mono uppercase text-[9px]">Veredicto Final</p>
                      <p className={`font-black uppercase text-sm ${
                        activity.desk_action === 'BUY' ? 'text-green-500' :
                        activity.desk_action === 'SELL' ? 'text-red-500' :
                        activity.desk_action === 'WAIT' || activity.desk_action === 'WATCH' ? 'text-yellow-500' :
                        'text-blue-400'
                      }`}>
                        {activity.desk_action === 'BUY' ? 'COMPRAR / EJECUTAR' :
                         activity.desk_action === 'SELL' ? 'VENDER / LIQUIDAR' :
                         activity.desk_action === 'WAIT' || activity.desk_action === 'WATCH' ? 'OBSERVAR / EN ESPERA' :
                         activity.desk_action === 'HOLD' ? 'MANTENER POSICIÓN' :
                         activity.desk_action || 'SIN ACCIÓN'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </CardContent>
        )}
      </Card>
    );
  }

  // STANDALONE MODE: Full card (original behavior)
  return (
    <Card className="hover:border-zinc-700 transition-all bg-zinc-950/40">
      <div className="cursor-pointer" onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}>
        <CardHeader className="flex flex-row items-center justify-between py-6">
          <div className="flex items-center gap-4">
            <Badge variant={isBuy ? "success" : "secondary"} className="px-3 py-1">
              {activity.desk_action || 'WAIT'}
            </Badge>
            <div>
              <span className="text-2xl font-bold tracking-tighter text-zinc-100">{activity.ticker}</span>
              <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest mt-1">
                {activity.recommendation} • {currentStatus}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="text-xs text-zinc-500 font-mono uppercase">Tamaño de Posición</p>
              <p className="text-sm font-bold text-zinc-300">
                ${Number(activity.position_size || 0).toLocaleString()}
              </p>
            </div>
            {expanded ? <ChevronUp className="w-5 h-5 text-zinc-500" /> : <ChevronDown className="w-5 h-5 text-zinc-500" />}
          </div>
        </CardHeader>

        <CardContent className="pb-6">
          <div className="text-sm text-zinc-300 leading-relaxed mb-6 italic border-l-2 border-zinc-800 pl-4 py-1">
            &quot;{activity.rationale || activity.decision_notes}&quot;
          </div>

          <div className="flex flex-wrap gap-4">
            <QuantItem label="RSI" value={quant.rsi_14} />
            <QuantItem label="Beta" value={quant.beta_spy} />
            <QuantItem label="RVOL" value={quant.rvol} />
            <QuantItem label="Corr SPY" value={quant.corr_spy_20d} />
            <QuantItem label="Sentiment" value={(activity.sentiment_score !== null && activity.sentiment_score !== undefined) ? `${(activity.sentiment_score * 100).toFixed(1)}%` : '--'} />
            <QuantItem label="Final Score" value={(activity.confidence_in_decision !== null && activity.confidence_in_decision !== undefined) ? `${(activity.confidence_in_decision * 100).toFixed(0)}%` : '--'} />
          </div>
        </CardContent>

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
                {bullCase.arguments && bullCase.arguments.length > 0 ? (
                  bullCase.arguments.map((arg: string, i: number) => (
                    <li key={i} className="text-[11px] text-zinc-400 flex gap-2">
                      <span className="text-green-900 font-bold">•</span> {arg}
                    </li>
                  ))
                ) : (
                  <li className="text-[11px] text-zinc-600 italic">No positive signals detected in recent news</li>
                )}
              </ul>

              {/* EVIDENCE CHAIN: NEWS → ENTITY */}
              {bullCase.evidence_chain && bullCase.evidence_chain.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-[9px] font-mono uppercase text-zinc-600">📰 Source News</p>
                  {bullCase.evidence_chain.map((evidence: any, i: number) => (
                    <div key={i} className="bg-zinc-900/50 p-2 rounded border-l-2 border-green-700">
                      <p className="text-[10px] text-zinc-400 font-mono truncate" title={evidence.news_title}>
                        "{evidence.news_title}"
                      </p>
                      <p className="text-[9px] text-zinc-500 mt-1">
                        <span className="text-green-700">→</span> {evidence.entity_name} ({evidence.impact}, {Math.round(evidence.confidence * 100)}% conf)
                        <span className="text-zinc-600 ml-2">[{evidence.news_source}]</span>
                      </p>
                    </div>
                  ))}
                </div>
              )}

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

              {/* EVIDENCE CHAIN: NEWS → ENTITY */}
              {bearCase.evidence_chain && bearCase.evidence_chain.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-[9px] font-mono uppercase text-zinc-600">📰 Source News</p>
                  {bearCase.evidence_chain.map((evidence: any, i: number) => (
                    <div key={i} className="bg-zinc-900/50 p-2 rounded border-l-2 border-red-700">
                      <p className="text-[10px] text-zinc-400 font-mono truncate" title={evidence.news_title}>
                        "{evidence.news_title}"
                      </p>
                      <p className="text-[9px] text-zinc-500 mt-1">
                        <span className="text-red-700">→</span> {evidence.entity_name} ({evidence.impact}, {Math.round(evidence.confidence * 100)}% conf)
                        <span className="text-zinc-600 ml-2">[{evidence.news_source}]</span>
                      </p>
                    </div>
                  ))}
                </div>
              )}

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
                <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Estrategia de Riesgo</h3>
              </div>
              <div className="bg-zinc-900/30 p-4 rounded-xl border border-zinc-900 space-y-3">
                <div className="flex justify-between text-xs">
                  <span className="text-zinc-500 font-mono">STOP_LOSS</span>
                  <span className="text-red-500 font-bold">{riskAnalysis.stop_loss?.percentage * 100 || 5}%</span>
                </div>
                <p className="text-[10px] text-zinc-500 italic leading-snug">
                  Defensa: {riskAnalysis.stop_loss?.technical_defense || "Protección estándar de varianza."}
                </p>
              </div>
              {riskAnalysis.deep_analysis && (
                <div className="p-3 bg-yellow-950/5 rounded border border-yellow-900/20">
                  <p className="text-[9px] text-yellow-700 font-mono uppercase mb-1 font-bold">Raciocinio de Riesgo</p>
                  <p className="text-[10px] text-zinc-400 leading-relaxed">{riskAnalysis.deep_analysis}</p>
                </div>
              )}
            </div>

              {/* RISK & EXECUTION PANEL */}
              <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-zinc-900">
                
                {/* RISK STRATEGY */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-yellow-500">
                    <ShieldCheck className="w-4 h-4" />
                    <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Perfil de Riesgo</h3>
                  </div>

                  <div className="bg-zinc-900/30 rounded-2xl border border-zinc-900 overflow-hidden">
                    <div className="p-4 border-b border-zinc-900 flex justify-between items-center bg-yellow-950/5">
                      <span className="text-[10px] font-mono text-zinc-500 uppercase">Red de Seguridad</span>
                      <div className="text-right">
                        <span className="text-xs font-bold text-red-500 font-mono">STOP LOSS @ {riskAnalysis.stop_loss?.percentage * 100 || 5}%</span>
                      </div>
                    </div>
                    <div className="p-4 space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="mt-1 p-1 bg-zinc-900 rounded">
                          <AlertTriangle className="w-3 h-3 text-zinc-600" />
                        </div>
                        <p className="text-[11px] text-zinc-400 leading-relaxed italic">
                          "{riskAnalysis.deep_analysis || riskAnalysis.stop_loss?.technical_defense || "Protección estándar de varianza aplicada basada en la volatilidad del activo."}"
                        </p>
                      </div>
                      <div className="flex gap-2 pt-2">
                        <Badge variant="outline" className="text-[8px] bg-zinc-950 border-zinc-800 text-zinc-500">RSI: {quant.rsi_14?.toFixed(1)}</Badge>
                        <Badge variant="outline" className="text-[8px] bg-zinc-950 border-zinc-800 text-zinc-500">ATR: ${quant.atr_14?.toFixed(2)}</Badge>
                        <Badge variant="outline" className={`text-[8px] bg-zinc-950 border-zinc-800 ${activity.recommendation === 'BUY' ? 'text-green-500' : 'text-yellow-500'}`}>
                          NVL: {activity.recommendation === 'BUY' ? 'AGRESIVO' : 'CAUTELOSO'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>

                {/* ORDER TICKET (EXECUTION) */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-purple-500">
                    <Zap className="w-4 h-4" />
                    <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Ticket de Orden</h3>
                  </div>

                  <div className="bg-purple-950/5 rounded-2xl border border-purple-900/20 p-5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                      <Target className="w-12 h-12 text-purple-500" />
                    </div>

                    <div className="space-y-4 relative z-10">
                      <div className="flex justify-between items-end">
                        <div>
                          <p className="text-[9px] font-mono text-purple-500 uppercase mb-1">Asignación</p>
                          <p className="text-2xl font-black text-zinc-100 font-mono">
                            {activity.position_size ? `$${activity.position_size.toLocaleString()}` : '$0.00'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-[9px] font-mono text-zinc-600 uppercase mb-1">Objetivo de Entrada</p>
                          <p className="text-sm font-bold text-zinc-400 font-mono">
                            {activity.entry_price ? `$${activity.entry_price.toFixed(2)}` : 'MERCADO'}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-purple-900/20">
                        <div>
                          <p className="text-[8px] font-mono text-zinc-600 uppercase mb-1">Referencia del Broker</p>
                          <p className="text-[10px] font-mono text-zinc-400 truncate">
                            {activity.alpaca_order_id || '---'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-[8px] font-mono text-zinc-600 uppercase mb-1">Estado</p>
                          <Badge className={`text-[9px] font-mono font-bold ${
                            currentStatus === 'FILLED' ? 'bg-green-500/10 text-green-500 border-green-500/20' :
                            currentStatus === 'PENDING' || currentStatus === 'NEW' ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                            'bg-zinc-800 text-zinc-500 border-zinc-700'
                          }`}>
                            {currentStatus || 'ESPERA'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* CIO FINAL RATIONALE DETAILS */}
              <div className="space-y-4 md:col-span-2 pt-6 border-t border-zinc-900">
                <div className="flex items-center gap-2 text-blue-500">
                  <BrainCircuit className="w-4 h-4" />
                  <h3 className="text-xs font-bold uppercase tracking-widest font-mono">Resumen de Inteligencia Estratégica</h3>
                </div>
                <div className="bg-blue-950/5 border border-blue-900/20 rounded-xl p-5">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-6 text-[11px] items-center">
                    <div className="md:col-span-2 space-y-1">
                      <p className="text-zinc-500 font-mono uppercase text-[9px]">Motor de Decisión</p>
                      <p className="text-zinc-300 font-bold">GLM-5.1 Strategic Brain</p>
                    </div>

                    <div className="md:col-span-7 space-y-1 border-l border-blue-900/20 pl-6">
                      <p className="text-zinc-500 font-mono uppercase text-[9px]">Razón de Ejecución y Contexto</p>
                      <p className="text-[11px] text-zinc-300 leading-relaxed font-mono italic">
                        "{activity.decision_notes || 'No se proporcionó contexto adicional de decisión por el modelo.'}"
                      </p>
                    </div>

                    <div className="md:col-span-3 space-y-1 border-l border-blue-900/20 pl-6 text-right">
                      <p className="text-zinc-500 font-mono uppercase text-[9px]">Veredicto Final</p>
                      <p className={`font-black uppercase text-sm ${
                        activity.desk_action === 'BUY' ? 'text-green-500' :
                        activity.desk_action === 'SELL' ? 'text-red-500' :
                        activity.desk_action === 'WAIT' || activity.desk_action === 'WATCH' ? 'text-yellow-500' :
                        'text-blue-400'
                      }`}>
                        {activity.desk_action === 'BUY' ? 'COMPRAR / EJECUTAR' :
                         activity.desk_action === 'SELL' ? 'VENDER / LIQUIDAR' :
                         activity.desk_action === 'WAIT' || activity.desk_action === 'WATCH' ? 'OBSERVAR / EN ESPERA' :
                         activity.desk_action === 'HOLD' ? 'MANTENER POSICIÓN' :
                         activity.desk_action || 'SIN ACCIÓN'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

          </div>
        </CardContent>
      )}
      </div>
    </Card>
  );
}

function QuantItem({ label, value }: any) {
  const displayValue = typeof value === 'number' ? value.toFixed(2) : value;
  return (
    <div className="bg-zinc-900/30 px-4 py-3 rounded-xl border border-zinc-900/80 flex flex-col min-w-[110px] shadow-sm hover:bg-zinc-900/50 transition-colors">
      <span className="text-[10px] font-bold font-mono text-zinc-500 uppercase mb-1.5 tracking-[0.1em]">{label}</span>
      <span className="text-base font-black text-zinc-100 font-mono">{displayValue || '--'}</span>
    </div>
  );
}
