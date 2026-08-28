import React from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { 
  complaintCategories, 
  complaintStatuses, 
  complaintPriorities 
} from '../data/mockComplaints';
import { 
  AlertCircle, 
  Clock, 
  Shield, 
  User, 
  CreditCard, 
  Layers, 
  FilterX, 
  ChevronRight,
  Sparkles,
  Building,
  Landmark,
  ArrowUpDown
} from 'lucide-react';

export const ComplaintQueue = () => {
  const { 
    filteredComplaints, 
    selectedComplaintId, 
    setSelectedComplaintId,
    selectedProduct, 
    setSelectedProduct,
    selectedStatus, 
    setSelectedStatus,
    selectedPriority, 
    setSelectedPriority,
    setSearchQuery,
    searchQuery
  } = useWorkbench();

  const resetFilters = () => {
    setSelectedProduct('All Products');
    setSelectedStatus('All Statuses');
    setSelectedPriority('All Priorities');
    setSearchQuery('');
  };

  const hasActiveFilters = 
    selectedProduct !== 'All Products' || 
    selectedStatus !== 'All Statuses' || 
    selectedPriority !== 'All Priorities' || 
    searchQuery !== '';

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'Critical':
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-bold bg-rose-100 text-rose-700 dark:bg-rose-950/80 dark:text-rose-300 border border-rose-200 dark:border-rose-900"><span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse" /> Critical</span>;
      case 'High':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-orange-100 text-orange-700 dark:bg-orange-950/80 dark:text-orange-300 border border-orange-200 dark:border-orange-900">High</span>;
      case 'Medium':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium bg-amber-100 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-200 dark:border-amber-900">Medium</span>;
      default:
        return <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">Low</span>;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'New':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border border-blue-200 dark:border-blue-800">New Intake</span>;
      case 'Under Investigation':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">Investigating</span>;
      case 'Pending Customer':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border border-amber-200 dark:border-amber-800">Pending Info</span>;
      case 'Escalated':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 border border-purple-200 dark:border-purple-800">Escalated</span>;
      case 'Resolved':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">Resolved</span>;
      default:
        return null;
    }
  };

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'Private Client':
        return <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200 border border-amber-300 dark:border-amber-700">PRIVATE CLIENT</span>;
      case 'Commercial':
        return <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-200 border border-indigo-300 dark:border-indigo-700">COMMERCIAL</span>;
      case 'Preferred':
        return <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200">PREFERRED</span>;
      default:
        return <span className="px-1.5 py-0.2 rounded text-[10px] font-normal text-slate-500 dark:text-slate-400">STANDARD</span>;
    }
  };

  const formatSlaCountdown = (deadlineStr, status) => {
    if (status === 'Resolved') return <span className="text-emerald-600 dark:text-emerald-400 font-medium">Met SLA</span>;
    
    const now = new Date();
    const deadline = new Date(deadlineStr);
    const diffHours = Math.round((deadline - now) / (1000 * 60 * 60));

    if (diffHours < 0) {
      return (
        <span className="inline-flex items-center gap-1 text-rose-600 dark:text-rose-400 font-bold">
          <Clock className="h-3 w-3 animate-spin" />
          Breached ({Math.abs(diffHours)}h ago)
        </span>
      );
    }
    if (diffHours <= 12) {
      return (
        <span className="inline-flex items-center gap-1 text-rose-600 dark:text-rose-400 font-bold">
          <Clock className="h-3 w-3" />
          Due in {diffHours}h
        </span>
      );
    }
    if (diffHours <= 36) {
      return (
        <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400 font-medium">
          <Clock className="h-3 w-3" />
          Due in {diffHours}h
        </span>
      );
    }
    const days = Math.round(diffHours / 24);
    return (
      <span className="inline-flex items-center gap-1 text-slate-500 dark:text-slate-400">
        <Clock className="h-3 w-3" />
        Due in {days} days
      </span>
    );
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col h-full overflow-hidden transition-colors">
      
      {/* Filter Control Header */}
      <div className="p-4 border-b border-slate-100 dark:border-slate-800/80 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="flex flex-wrap items-center gap-2.5">
          
          {/* Product Filter */}
          <div className="relative">
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium rounded-xl px-3 py-1.5 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              {complaintCategories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="relative">
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium rounded-xl px-3 py-1.5 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              {complaintStatuses.map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          {/* Priority Filter */}
          <div className="relative">
            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium rounded-xl px-3 py-1.5 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              {complaintPriorities.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          {/* Reset Filters */}
          {hasActiveFilters && (
            <button
              onClick={resetFilters}
              className="flex items-center gap-1 text-xs text-rose-600 dark:text-rose-400 hover:underline px-2 py-1 font-medium"
            >
              <FilterX className="h-3.5 w-3.5" />
              Reset Filters
            </button>
          )}
        </div>

        {/* Count Label */}
        <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
          Showing <span className="font-bold text-slate-800 dark:text-slate-100 font-mono">{filteredComplaints.length}</span> disputes
        </div>
      </div>

      {/* Table / Queue List */}
      <div className="overflow-x-auto flex-1 max-h-[700px] overflow-y-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-100 dark:border-slate-800 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider bg-slate-50/70 dark:bg-slate-900/80 sticky top-0 z-10 backdrop-blur-sm">
              <th className="py-3 px-4">Case / Customer</th>
              <th className="py-3 px-4">Product Category</th>
              <th className="py-3 px-4">Priority</th>
              <th className="py-3 px-4">Disputed Amt</th>
              <th className="py-3 px-4">Regulatory / SLA</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Assigned Specialist</th>
              <th className="py-3 px-2 text-right"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs">
            {filteredComplaints.length === 0 ? (
              <tr>
                <td colSpan="8" className="py-12 text-center text-slate-400">
                  <div className="max-w-xs mx-auto flex flex-col items-center">
                    <Layers className="h-8 w-8 text-slate-300 dark:text-slate-600 mb-2" />
                    <p className="font-semibold text-slate-700 dark:text-slate-300 text-sm">No complaints match filters</p>
                    <p className="text-xs mt-1">Try resetting the search terms or clearing the selected category filters.</p>
                    <button
                      onClick={resetFilters}
                      className="mt-3 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-300 text-xs font-semibold"
                    >
                      Clear All Filters
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              filteredComplaints.map((c) => {
                const isSelected = selectedComplaintId === c.id;
                return (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedComplaintId(c.id)}
                    className={`cursor-pointer transition-all duration-150 ${
                      isSelected
                        ? 'bg-blue-50/90 dark:bg-blue-950/40 border-l-4 border-l-blue-600 dark:border-l-blue-400'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/40 border-l-4 border-l-transparent'
                    }`}
                  >
                    {/* Case / Customer */}
                    <td className="py-3.5 px-4">
                      <div className="flex flex-col gap-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-blue-600 dark:text-blue-400 text-xs">
                            {c.id}
                          </span>
                          {getTierBadge(c.customerTier)}
                        </div>
                        <span className="font-semibold text-slate-900 dark:text-slate-100 text-sm truncate max-w-xs">
                          {c.customerName}
                        </span>
                        <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                          {c.accountNumber}
                        </span>
                      </div>
                    </td>

                    {/* Product */}
                    <td className="py-3.5 px-4">
                      <div className="flex flex-col">
                        <span className="font-medium text-slate-800 dark:text-slate-200">
                          {c.product}
                        </span>
                        <span className="text-[11px] text-slate-400 truncate max-w-[160px]">
                          {c.channel}
                        </span>
                      </div>
                    </td>

                    {/* Priority */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {getPriorityBadge(c.priority)}
                    </td>

                    {/* Disputed Amount */}
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-800 dark:text-slate-200">
                      {c.disputedAmount > 0 ? (
                        <span>${c.disputedAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                      ) : (
                        <span className="text-slate-400 font-normal">N/A ($0.00)</span>
                      )}
                    </td>

                    {/* Regulatory & SLA */}
                    <td className="py-3.5 px-4">
                      <div className="flex flex-col gap-1">
                        <div className="text-[11px]">
                          {formatSlaCountdown(c.slaDeadline, c.status)}
                        </div>
                        {c.regulatoryTag && c.regulatoryTag !== 'None' && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-200 dark:border-emerald-800/80">
                            <Shield className="h-2.5 w-2.5" />
                            {c.regulatoryTag}
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {getStatusBadge(c.status)}
                    </td>

                    {/* Assigned Specialist */}
                    <td className="py-3.5 px-4">
                      <span className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                        {c.assignedTo}
                      </span>
                    </td>

                    {/* Arrow Indicator */}
                    <td className="py-3.5 px-2 text-right">
                      <ChevronRight className={`h-4 w-4 transition-transform ${isSelected ? 'text-blue-600 dark:text-blue-400 translate-x-1' : 'text-slate-300 dark:text-slate-600'}`} />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
};
