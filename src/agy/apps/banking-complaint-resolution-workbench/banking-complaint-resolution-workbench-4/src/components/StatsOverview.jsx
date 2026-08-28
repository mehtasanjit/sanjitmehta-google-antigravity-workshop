import React from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { 
  AlertTriangle, 
  Clock, 
  ShieldAlert, 
  DollarSign, 
  CheckCircle2, 
  TrendingUp,
  Flame
} from 'lucide-react';

export const StatsOverview = () => {
  const { 
    complaints, 
    setSelectedStatus, 
    setSelectedPriority, 
    setSelectedProduct 
  } = useWorkbench();

  const totalActive = complaints.filter(c => c.status !== 'Resolved').length;
  const criticalCount = complaints.filter(c => c.priority === 'Critical' && c.status !== 'Resolved').length;
  const escalatedCount = complaints.filter(c => c.status === 'Escalated').length;
  const regulatoryCount = complaints.filter(c => c.regulatoryTag && c.regulatoryTag !== 'None').length;
  const resolvedCount = complaints.filter(c => c.status === 'Resolved').length;

  const totalDisputedAmount = complaints.reduce((sum, c) => sum + (Number(c.disputedAmount) || 0), 0);
  
  // Calculate approaching or breached SLA (< 24h)
  const now = new Date();
  const slaUrgentCount = complaints.filter(c => {
    if (c.status === 'Resolved') return false;
    const deadline = new Date(c.slaDeadline);
    const diffHours = (deadline - now) / (1000 * 60 * 60);
    return diffHours <= 24;
  }).length;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5 mb-6">
      
      {/* 1. Total Active Cases */}
      <div 
        onClick={() => { setSelectedStatus('All Statuses'); setSelectedPriority('All Priorities'); }}
        className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm hover:border-blue-500/50 dark:hover:border-blue-500/50 cursor-pointer transition-all group"
      >
        <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Active Queue</span>
          <div className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform">
            <TrendingUp className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-slate-900 dark:text-white">{totalActive}</span>
          <span className="text-xs text-slate-400 font-medium">cases</span>
        </div>
        <div className="mt-2 flex items-center gap-1.5 text-[11px] text-blue-600 dark:text-blue-400 font-medium">
          <span>{resolvedCount} resolved this cycle</span>
        </div>
      </div>

      {/* 2. Critical Urgency */}
      <div 
        onClick={() => setSelectedPriority('Critical')}
        className={`bg-white dark:bg-slate-900 p-4 rounded-2xl border shadow-sm cursor-pointer transition-all group ${
          criticalCount > 0 
            ? 'border-rose-200 dark:border-rose-900/60 bg-rose-50/20 dark:bg-rose-950/10 hover:border-rose-500' 
            : 'border-slate-200/80 dark:border-slate-800 hover:border-slate-400'
        }`}
      >
        <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-600 dark:text-rose-400">Critical Priority</span>
          <div className="p-1.5 rounded-lg bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400 group-hover:scale-110 transition-transform">
            <Flame className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-rose-600 dark:text-rose-400">{criticalCount}</span>
          {criticalCount > 0 && (
            <span className="px-1.5 py-0.5 rounded-full bg-rose-100 dark:bg-rose-900/80 text-[10px] font-bold text-rose-700 dark:text-rose-300 animate-urgent">
              Immediate
            </span>
          )}
        </div>
        <div className="mt-2 text-[11px] text-rose-500 font-medium">
          {escalatedCount} escalated to VP/Legal
        </div>
      </div>

      {/* 3. SLA At Risk / Breached */}
      <div 
        onClick={() => setSelectedStatus('Under Investigation')}
        className={`bg-white dark:bg-slate-900 p-4 rounded-2xl border shadow-sm cursor-pointer transition-all group ${
          slaUrgentCount > 0 
            ? 'border-amber-200 dark:border-amber-900/60 bg-amber-50/20 dark:bg-amber-950/10 hover:border-amber-500' 
            : 'border-slate-200/80 dark:border-slate-800'
        }`}
      >
        <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">SLA &lt; 24h</span>
          <div className="p-1.5 rounded-lg bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
            <Clock className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-amber-600 dark:text-amber-400">{slaUrgentCount}</span>
          <span className="text-xs text-amber-600/80 font-medium">deadlines</span>
        </div>
        <div className="mt-2 text-[11px] text-amber-600 dark:text-amber-400 font-medium">
          Reg E / CFPB Timers
        </div>
      </div>

      {/* 4. Regulatory & CFPB Flags */}
      <div 
        onClick={() => setSelectedStatus('All Statuses')}
        className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm hover:border-emerald-500/50 cursor-pointer transition-all group"
      >
        <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Compliance</span>
          <div className="p-1.5 rounded-lg bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform">
            <ShieldAlert className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">{regulatoryCount}</span>
          <span className="text-xs text-emerald-600/80 font-medium">mandates</span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400 font-medium">
          100% CFPB Audit Trail
        </div>
      </div>

      {/* 5. Total Disputed Amount */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm transition-all">
        <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Disputed Volume</span>
          <div className="p-1.5 rounded-lg bg-purple-50 dark:bg-purple-950 text-purple-600 dark:text-purple-400">
            <DollarSign className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-bold font-mono text-slate-900 dark:text-white">
            ${totalDisputedAmount.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </span>
        </div>
        <div className="mt-2 text-[11px] text-purple-600 dark:text-purple-400 font-medium">
          Under active review
        </div>
      </div>

      {/* 6. Resolution Adherence */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm transition-all">
        <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">SLA Adherence</span>
          <div className="p-1.5 rounded-lg bg-teal-50 dark:bg-teal-950 text-teal-600 dark:text-teal-400">
            <CheckCircle2 className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-teal-600 dark:text-teal-400">96.4%</span>
        </div>
        <div className="mt-2 text-[11px] text-teal-600 dark:text-teal-400 font-medium">
          Target: &gt;95.0%
        </div>
      </div>

    </div>
  );
};
