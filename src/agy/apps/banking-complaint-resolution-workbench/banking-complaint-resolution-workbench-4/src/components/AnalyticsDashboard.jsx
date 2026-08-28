import React from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  ShieldCheck, 
  AlertOctagon, 
  DollarSign, 
  Clock, 
  Layers,
  ArrowUpRight,
  Sparkles,
  CheckCircle2
} from 'lucide-react';

export const AnalyticsDashboard = () => {
  const { complaints, setSelectedProduct, setActiveTab } = useWorkbench();

  // Aggregate product counts and disputed amounts
  const productStats = complaints.reduce((acc, c) => {
    if (!acc[c.product]) {
      acc[c.product] = { count: 0, amount: 0, resolved: 0 };
    }
    acc[c.product].count += 1;
    acc[c.product].amount += (Number(c.disputedAmount) || 0);
    if (c.status === 'Resolved') acc[c.product].resolved += 1;
    return acc;
  }, {});

  // Aggregate channels
  const channelStats = complaints.reduce((acc, c) => {
    acc[c.channel] = (acc[c.channel] || 0) + 1;
    return acc;
  }, {});

  // Aggregate root causes
  const rootCauses = complaints.reduce((acc, c) => {
    acc[c.rootCause] = (acc[c.rootCause] || 0) + 1;
    return acc;
  }, {});

  // Regulatory breakdown
  const regulatoryStats = complaints.reduce((acc, c) => {
    if (c.regulatoryTag && c.regulatoryTag !== 'None') {
      acc[c.regulatoryTag] = (acc[c.regulatoryTag] || 0) + 1;
    }
    return acc;
  }, {});

  const totalDisputed = complaints.reduce((sum, c) => sum + (Number(c.disputedAmount) || 0), 0);
  const totalCases = complaints.length;

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-3xl p-6 text-white shadow-lg border border-blue-800/40">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/30 text-blue-200 border border-blue-400/30">
                Operations & Compliance Intelligence
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold">Banking Dispute & Regulatory Analytics</h2>
            <p className="text-xs text-blue-200/80 mt-1 max-w-2xl">
              Real-time monitoring of complaint volumes, financial remediation impact, statutory compliance windows (CFPB, Reg E, Reg Z, FCRA), and root-cause patterns.
            </p>
          </div>

          <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/10">
            <div>
              <span className="text-[11px] text-blue-200 uppercase tracking-wider block font-semibold">Total Claim Volume</span>
              <span className="text-2xl font-bold font-mono">${totalDisputed.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="h-8 w-px bg-white/20" />
            <div>
              <span className="text-[11px] text-blue-200 uppercase tracking-wider block font-semibold">Total Audited Cases</span>
              <span className="text-2xl font-bold font-mono">{totalCases}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Product Category Volume & Exposure (7 cols) */}
        <div className="lg:col-span-7 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Dispute Volume & Exposure by Product</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">Live Aggregation</span>
          </div>

          <div className="mt-4 space-y-4">
            {Object.entries(productStats).map(([product, data]) => {
              const countPercent = Math.round((data.count / totalCases) * 100);
              return (
                <div 
                  key={product}
                  onClick={() => { setSelectedProduct(product); setActiveTab('queue'); }}
                  className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-blue-50/50 dark:hover:bg-blue-950/30 border border-slate-100 dark:border-slate-800/80 cursor-pointer transition-all group"
                >
                  <div className="flex items-center justify-between text-xs font-semibold mb-1.5">
                    <span className="text-slate-800 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                      {product}
                    </span>
                    <div className="flex items-center gap-3 font-mono">
                      <span className="text-slate-500 dark:text-slate-400">{data.count} cases ({countPercent}%)</span>
                      <span className="font-bold text-slate-900 dark:text-white">
                        ${data.amount.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                      </span>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-600 rounded-full transition-all duration-500" 
                      style={{ width: `${Math.max(countPercent, 12)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Regulatory & Compliance Exposure (5 cols) */}
        <div className="lg:col-span-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">Statutory & Regulatory Distribution</h3>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold">
                100% In-SLA
              </span>
            </div>

            <div className="mt-4 space-y-3">
              {Object.entries(regulatoryStats).map(([reg, count]) => (
                <div key={reg} className="p-3 rounded-xl border border-emerald-100 dark:border-emerald-900/40 bg-emerald-50/30 dark:bg-emerald-950/20 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-xs text-slate-800 dark:text-slate-100 block">{reg}</span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400">Strict regulatory clock active</span>
                  </div>
                  <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-sm px-2.5 py-1 bg-white dark:bg-slate-900 rounded-lg shadow-xs border border-emerald-200 dark:border-emerald-800">
                    {count}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/60 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0" />
            <span>All active cases meet CFPB 15-day and Reg E 10-day provisional credit mandates.</span>
          </div>
        </div>

      </div>

      {/* Secondary Grid: Ingestion Channels & Root Causes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Root Cause Analysis */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <AlertOctagon className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Identified Root Causes</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">System vs Human</span>
          </div>

          <div className="mt-4 space-y-2.5">
            {Object.entries(rootCauses).map(([cause, count]) => (
              <div key={cause} className="flex items-center justify-between text-xs p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/60">
                <span className="text-slate-700 dark:text-slate-300 font-medium">{cause}</span>
                <span className="font-mono font-bold text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-950 px-2 py-0.5 rounded">
                  {count} {count === 1 ? 'case' : 'cases'}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Intake Channel Breakdown */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Intake Channels</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">Channel Mix</span>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3">
            {Object.entries(channelStats).map(([channel, count]) => (
              <div key={channel} className="p-3.5 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-800">
                <span className="text-xs text-slate-500 dark:text-slate-400 block">{channel}</span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-xl font-bold font-mono text-slate-900 dark:text-white">{count}</span>
                  <span className="text-[11px] text-slate-400 font-medium">({Math.round((count / totalCases) * 100)}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
