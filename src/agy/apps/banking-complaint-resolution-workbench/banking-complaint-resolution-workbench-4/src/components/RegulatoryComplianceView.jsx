import React from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { 
  ShieldCheck, 
  Scale, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  FileText, 
  ExternalLink,
  BookOpen,
  ArrowRight
} from 'lucide-react';

export const RegulatoryComplianceView = () => {
  const { complaints, setSelectedComplaintId, setActiveTab } = useWorkbench();

  const regulatoryComplaints = complaints.filter(
    c => c.regulatoryTag && c.regulatoryTag !== 'None'
  );

  const handleSelectCase = (id) => {
    setSelectedComplaintId(id);
    setActiveTab('queue');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Overview Banner */}
      <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 rounded-3xl p-6 text-white shadow-lg border border-emerald-800/40">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5" />
                Federal & State Regulatory Portal
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold">CFPB & Statutory Compliance Auditing</h2>
            <p className="text-xs text-emerald-200/80 mt-1 max-w-2xl">
              Automated tracking of mandatory response clocks, provisional credit deadlines, and regulatory reporting for Consumer Financial Protection Bureau (CFPB), Federal Reserve, and OCC oversight.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-white/10 backdrop-blur-md px-4 py-3 rounded-2xl border border-white/10 text-center">
              <span className="text-[11px] text-emerald-200 uppercase tracking-wider block font-semibold">Active Reg Cases</span>
              <span className="text-2xl font-bold font-mono text-emerald-300">{regulatoryComplaints.length}</span>
            </div>
            <div className="bg-white/10 backdrop-blur-md px-4 py-3 rounded-2xl border border-white/10 text-center">
              <span className="text-[11px] text-emerald-200 uppercase tracking-wider block font-semibold">Audit Health</span>
              <span className="text-2xl font-bold font-mono text-white">100%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Statutory Guidelines Reference Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Reg E */}
        <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-bold text-xs mb-1">
            <Scale className="h-4 w-4" />
            <span>Regulation E (12 CFR § 1005)</span>
          </div>
          <span className="text-[11px] font-semibold text-slate-800 dark:text-slate-200 block">Electronic Fund Transfers</span>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-normal">
            Mandates investigation completion within 10 business days or provisional credit issuance with up to 45/90 day extension.
          </p>
        </div>

        {/* Reg Z */}
        <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-xs mb-1">
            <Scale className="h-4 w-4" />
            <span>Regulation Z (12 CFR § 1026)</span>
          </div>
          <span className="text-[11px] font-semibold text-slate-800 dark:text-slate-200 block">Truth in Lending / Card Disputes</span>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-normal">
            Requires acknowledgment within 30 days and full resolution within 2 complete billing cycles (max 90 days).
          </p>
        </div>

        {/* FCRA */}
        <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 font-bold text-xs mb-1">
            <Scale className="h-4 w-4" />
            <span>FCRA (15 U.S.C. § 1681)</span>
          </div>
          <span className="text-[11px] font-semibold text-slate-800 dark:text-slate-200 block">Fair Credit Reporting Act</span>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-normal">
            Requires furnishers of credit data to investigate direct disputes and report modifications to Equifax, Experian, and TransUnion in 30 days.
          </p>
        </div>

        {/* CFPB Portal */}
        <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-xs mb-1">
            <Scale className="h-4 w-4" />
            <span>CFPB Portal Mandate</span>
          </div>
          <span className="text-[11px] font-semibold text-slate-800 dark:text-slate-200 block">15-Day Expedited Response</span>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-normal">
            Requires substantive official responses submitted via Company Portal within 15 calendar days to avoid formal enforcement scrutiny.
          </p>
        </div>

      </div>

      {/* Regulated Case Audit Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Active Regulatory Audit Cases</h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {regulatoryComplaints.length} cases flagged for regulatory scrutiny
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900 text-slate-400 font-semibold uppercase text-[10px]">
                <th className="py-3 px-4">Dispute ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Statutory Category</th>
                <th className="py-3 px-4">Disputed Amt</th>
                <th className="py-3 px-4">SLA Window</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {regulatoryComplaints.map(c => (
                <tr key={c.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-blue-600 dark:text-blue-400">
                    {c.id}
                  </td>
                  <td className="py-3 px-4 font-semibold text-slate-800 dark:text-slate-200">
                    {c.customerName}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-md border border-emerald-200 dark:border-emerald-800">
                      <ShieldCheck className="h-3 w-3" />
                      {c.regulatoryTag}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono font-semibold text-slate-800 dark:text-slate-200">
                    {c.disputedAmount > 0 ? `$${c.disputedAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : '$0.00'}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600 dark:text-slate-300">
                    {new Date(c.slaDeadline).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {c.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleSelectCase(c.id)}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950 dark:hover:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-lg text-xs font-bold transition-all"
                    >
                      <span>Open Workspace</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
