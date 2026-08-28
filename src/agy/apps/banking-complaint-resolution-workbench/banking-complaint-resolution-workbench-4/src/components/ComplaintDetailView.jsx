import React, { useState } from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { mockAgents, complaintStatuses, complaintPriorities } from '../data/mockComplaints';
import { AiResolutionCopilot } from './AiResolutionCopilot';
import { 
  User, 
  CreditCard, 
  Phone, 
  Mail, 
  Calendar, 
  DollarSign, 
  ShieldAlert, 
  Send, 
  CheckCircle, 
  AlertTriangle, 
  FileText, 
  MessageSquare, 
  Activity, 
  Sparkles,
  ArrowRight,
  Landmark,
  BadgeAlert,
  Clock
} from 'lucide-react';

export const ComplaintDetailView = () => {
  const { 
    selectedComplaint, 
    updateComplaintStatus, 
    assignComplaint, 
    addTimelineNote, 
    issueRemediation,
    resolveComplaint,
    showToast
  } = useWorkbench();

  const [newNote, setNewNote] = useState('');
  const [noteType, setNoteType] = useState('agent_note');
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [resolveSummary, setResolveSummary] = useState('');
  const [refundInput, setRefundInput] = useState('');

  if (!selectedComplaint) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-12 text-center h-full flex flex-col items-center justify-center">
        <FileText className="h-12 w-12 text-slate-300 dark:text-slate-700 mb-3" />
        <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">No Dispute Selected</h3>
        <p className="text-xs text-slate-400 mt-1">Select a complaint from the queue on the left to inspect customer profile, audit history, and AI resolution tools.</p>
      </div>
    );
  }

  const handleAddNote = (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    addTimelineNote(selectedComplaint.id, newNote, noteType);
    setNewNote('');
  };

  const handleExecuteRemediation = () => {
    if (selectedComplaint.recommendedRemediation) {
      issueRemediation(selectedComplaint.id, selectedComplaint.recommendedRemediation);
    }
  };

  const handleResolveSubmit = (e) => {
    e.preventDefault();
    resolveComplaint(
      selectedComplaint.id, 
      resolveSummary || 'Standard case resolution following internal review.', 
      Number(refundInput) || (selectedComplaint.recommendedRemediation?.amount || 0)
    );
    setShowResolveModal(false);
    setResolveSummary('');
    setRefundInput('');
  };

  return (
    <div className="flex flex-col gap-5 h-full">
      
      {/* 1. Header Toolbar & Quick Actions */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm transition-colors">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5 mb-1.5">
              <span className="font-mono text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950 px-2.5 py-1 rounded-lg border border-blue-200 dark:border-blue-900">
                {selectedComplaint.id}
              </span>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                {selectedComplaint.product}
              </span>
              {selectedComplaint.regulatoryTag && (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 flex items-center gap-1">
                  <ShieldAlert className="h-3 w-3" />
                  {selectedComplaint.regulatoryTag}
                </span>
              )}
            </div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white leading-snug">
              {selectedComplaint.title}
            </h2>
            <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
              <span>Opened {new Date(selectedComplaint.createdAt).toLocaleDateString()}</span>
              <span>•</span>
              <span>Channel: {selectedComplaint.channel}</span>
              <span>•</span>
              <span className="font-mono">SLA Target: {new Date(selectedComplaint.slaDeadline).toLocaleDateString()}</span>
            </div>
          </div>

          {/* Status & Assignment controls */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Status Select */}
            <div className="flex flex-col">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Status</label>
              <select
                value={selectedComplaint.status}
                onChange={(e) => updateComplaintStatus(selectedComplaint.id, e.target.value)}
                className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold rounded-xl px-3 py-1.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer"
              >
                {complaintStatuses.filter(s => s !== 'All Statuses').map(st => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </select>
            </div>

            {/* Assignee Select */}
            <div className="flex flex-col">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Assigned Agent</label>
              <select
                value={selectedComplaint.assignedTo}
                onChange={(e) => assignComplaint(selectedComplaint.id, e.target.value)}
                className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium rounded-xl px-3 py-1.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer"
              >
                <option value="Unassigned">Unassigned</option>
                {mockAgents.map(a => (
                  <option key={a.id} value={a.name}>{a.name}</option>
                ))}
              </select>
            </div>

            {/* Resolve Case Button */}
            {selectedComplaint.status !== 'Resolved' && (
              <div className="flex flex-col justify-end">
                <label className="text-[10px] opacity-0 mb-0.5">Action</label>
                <button
                  onClick={() => {
                    setRefundInput(selectedComplaint.recommendedRemediation?.amount?.toString() || '0');
                    setShowResolveModal(true);
                  }}
                  className="flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-xs font-bold rounded-xl shadow-sm transition-all"
                >
                  <CheckCircle className="h-4 w-4" />
                  <span>Resolve & Close</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 2. Customer Profile & Dispute Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* Customer Intelligence Card */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-4 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800/80">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 rounded-lg">
                <User className="h-4 w-4" />
              </div>
              <span className="font-bold text-xs text-slate-900 dark:text-slate-100">Customer Profile</span>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
              {selectedComplaint.customerTier}
            </span>
          </div>

          <div className="mt-3 space-y-2.5 text-xs">
            <div>
              <span className="text-slate-400 text-[11px] block">Customer Name</span>
              <span className="font-bold text-slate-900 dark:text-slate-100 text-sm">{selectedComplaint.customerName}</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-400 text-[11px] block">Account Number</span>
                <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{selectedComplaint.accountNumber}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Relationship Tenure</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{selectedComplaint.customerTenure}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-400 text-[11px] block">Total Balance</span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{selectedComplaint.accountBalance}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Risk Rating</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{selectedComplaint.customerRiskScore}</span>
              </div>
            </div>
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800/60 flex flex-col gap-1 text-[11px] text-slate-500">
              <div className="flex items-center gap-1.5 truncate">
                <Mail className="h-3.5 w-3.5 text-slate-400" />
                <span className="truncate">{selectedComplaint.email}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Phone className="h-3.5 w-3.5 text-slate-400" />
                <span>{selectedComplaint.phone}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dispute Details & Disputed Amount */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-4 shadow-sm md:col-span-2">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800/80">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-rose-50 dark:bg-rose-950 text-rose-600 dark:text-rose-400 rounded-lg">
                <CreditCard className="h-4 w-4" />
              </div>
              <span className="font-bold text-xs text-slate-900 dark:text-slate-100">Dispute Narrative & Root Cause</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Disputed Amount:</span>
              <span className="font-mono font-bold text-base text-rose-600 dark:text-rose-400">
                ${selectedComplaint.disputedAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          <div className="mt-3">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Identified Root Cause:</span>
              <span className="px-2 py-0.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                {selectedComplaint.rootCause}
              </span>
              <span className="text-[11px] font-semibold text-slate-400 uppercase ml-2">Customer Sentiment:</span>
              <span className="px-2 py-0.5 rounded-lg text-xs font-medium bg-amber-50 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-900">
                {selectedComplaint.sentiment}
              </span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-950/60 rounded-xl border border-slate-200/60 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-normal">
              "{selectedComplaint.narrative}"
            </div>

            {/* Quick Remediation Banner */}
            {selectedComplaint.recommendedRemediation && (
              <div className="mt-3 p-3 bg-blue-50/70 dark:bg-blue-950/30 rounded-xl border border-blue-200 dark:border-blue-900/60 flex items-center justify-between gap-3">
                <div className="flex items-start gap-2.5">
                  <Sparkles className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="text-xs font-bold text-blue-950 dark:text-blue-200 block">
                      Recommended Remediation: {selectedComplaint.recommendedRemediation.action}
                    </span>
                    <span className="text-[11px] text-blue-700 dark:text-blue-300">
                      {selectedComplaint.recommendedRemediation.regulationBasis}
                    </span>
                  </div>
                </div>
                <button
                  onClick={handleExecuteRemediation}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold whitespace-nowrap shadow-sm transition-all"
                >
                  Authorize Action
                </button>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* 3. AI Copilot Panel & Audit Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: AI Resolution Copilot (5 cols) */}
        <div className="lg:col-span-5">
          <AiResolutionCopilot complaint={selectedComplaint} />
        </div>

        {/* Right: Comprehensive Audit & Timeline Trail (7 cols) */}
        <div className="lg:col-span-7 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">Regulatory Audit Trail & Case Timeline</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">
                {selectedComplaint.timeline.length} Events Logged
              </span>
            </div>

            {/* Timeline Stream */}
            <div className="mt-4 space-y-4 max-h-[380px] overflow-y-auto pr-2">
              {selectedComplaint.timeline.map((event, idx) => {
                let badgeColor = "bg-blue-500";
                let icon = <FileText className="h-3 w-3 text-white" />;
                if (event.type === 'system_event') {
                  badgeColor = "bg-purple-500";
                  icon = <Sparkles className="h-3 w-3 text-white" />;
                } else if (event.type === 'complaint_filed') {
                  badgeColor = "bg-amber-500";
                  icon = <AlertTriangle className="h-3 w-3 text-white" />;
                } else if (event.type === 'compliance_audit') {
                  badgeColor = "bg-emerald-500";
                  icon = <CheckCircle className="h-3 w-3 text-white" />;
                }

                return (
                  <div key={event.id || idx} className="relative flex items-start gap-3 pl-1">
                    {/* Timeline vertical bar */}
                    {idx !== selectedComplaint.timeline.length - 1 && (
                      <div className="absolute left-3.5 top-6 bottom-[-16px] w-0.5 bg-slate-200 dark:bg-slate-800" />
                    )}

                    <div className={`h-6 w-6 rounded-full ${badgeColor} flex items-center justify-center flex-shrink-0 z-10 shadow-sm`}>
                      {icon}
                    </div>

                    <div className="flex-1 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-800">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                          {event.author}
                        </span>
                        <span className="text-[11px] font-mono text-slate-400">
                          {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {new Date(event.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                        {event.content}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Add Note Form */}
          <form onSubmit={handleAddNote} className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Log Entry Type:</span>
              <select
                value={noteType}
                onChange={(e) => setNoteType(e.target.value)}
                className="text-xs bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-700 dark:text-slate-300 font-medium focus:outline-none"
              >
                <option value="agent_note">Internal Investigator Note</option>
                <option value="system_event">System Transaction Verification</option>
                <option value="compliance_audit">CFPB / Regulatory Compliance Audit</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Type internal note, investigator log, or compliance action..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                className="flex-1 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 font-medium"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-sm transition-all"
              >
                <Send className="h-3.5 w-3.5" />
                <span>Log Note</span>
              </button>
            </div>
          </form>
        </div>

      </div>

      {/* Resolve Case Modal */}
      {showResolveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800">
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">
              Finalize & Resolve Dispute #{selectedComplaint.id}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Closing this case will mark the dispute as resolved, record regulatory compliance fulfillment, and post the final audit note.
            </p>

            <form onSubmit={handleResolveSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Settlement / Refund Credit Amount ($)
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-mono">$</span>
                  <input
                    type="number"
                    step="0.01"
                    value={refundInput}
                    onChange={(e) => setRefundInput(e.target.value)}
                    className="w-full pl-7 pr-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono font-bold text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Resolution Executive Summary
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="Summarize root cause fix, customer communication outcome, and policy adherence..."
                  value={resolveSummary}
                  onChange={(e) => setResolveSummary(e.target.value)}
                  className="w-full p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowResolveModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-500/20"
                >
                  Confirm & Close Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
