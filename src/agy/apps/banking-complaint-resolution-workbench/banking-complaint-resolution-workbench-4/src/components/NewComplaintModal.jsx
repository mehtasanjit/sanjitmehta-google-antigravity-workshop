import React, { useState } from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { 
  complaintCategories, 
  complaintPriorities, 
  mockAgents 
} from '../data/mockComplaints';
import { X, PlusCircle, User, CreditCard, Shield, AlertTriangle } from 'lucide-react';

export const NewComplaintModal = () => {
  const { isNewModalOpen, setIsNewModalOpen, addComplaint, currentAgent } = useWorkbench();

  const [formData, setFormData] = useState({
    customerName: '',
    accountNumber: '',
    customerTier: 'Standard',
    email: '',
    phone: '',
    customerTenure: '2 years',
    customerRiskScore: 'Low (15/100)',
    accountBalance: '$12,500.00',
    title: '',
    product: 'Credit Cards',
    channel: 'Branch',
    priority: 'Medium',
    disputedAmount: '',
    regulatoryTag: 'None',
    rootCause: 'Under Investigation',
    assignedTo: currentAgent,
    sentiment: 'Upset / Inquiring',
    narrative: '',
    slaDays: 3
  });

  if (!isNewModalOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    const slaDate = new Date();
    slaDate.setDate(slaDate.getDate() + (Number(formData.slaDays) || 3));

    addComplaint({
      ...formData,
      disputedAmount: Number(formData.disputedAmount) || 0,
      slaDeadline: slaDate.toISOString(),
      recommendedRemediation: formData.disputedAmount > 0 ? {
        action: `Review and evaluate ${formData.product} dispute claim`,
        amount: Number(formData.disputedAmount) || 0,
        regulationBasis: formData.regulatoryTag !== 'None' ? formData.regulatoryTag : 'Standard Bank Dispute Policy'
      } : null
    });

    setIsNewModalOpen(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 rounded-xl">
              <PlusCircle className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900 dark:text-white">Intake New Dispute / Complaint</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">Log customer dispute for immediate triage and regulatory SLA tracking</p>
            </div>
          </div>
          <button
            onClick={() => setIsNewModalOpen(false)}
            className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4 text-xs">
          
          {/* Customer Details Row */}
          <div className="p-3.5 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800 space-y-3">
            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">Customer Details</span>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Customer Full Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Samantha Miller"
                  value={formData.customerName}
                  onChange={(e) => setFormData({ ...formData, customerName: e.target.value })}
                  className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Account Number *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. ACC-491029-77"
                  value={formData.accountNumber}
                  onChange={(e) => setFormData({ ...formData, accountNumber: e.target.value })}
                  className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl font-mono text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Customer Tier</label>
                <select
                  value={formData.customerTier}
                  onChange={(e) => setFormData({ ...formData, customerTier: e.target.value })}
                  className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  <option value="Standard">Standard</option>
                  <option value="Preferred">Preferred</option>
                  <option value="Private Client">Private Client</option>
                  <option value="Commercial">Commercial</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Email Address</label>
                <input
                  type="email"
                  placeholder="customer@email.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Phone Number</label>
                <input
                  type="tel"
                  placeholder="+1 (555) 000-0000"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>
          </div>

          {/* Dispute Details */}
          <div className="space-y-3">
            <div>
              <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Dispute Subject / Headline *</label>
              <input
                type="text"
                required
                placeholder="e.g. Unauthorized Debit Card Charge at Overseas Merchant"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Product Category</label>
                <select
                  value={formData.product}
                  onChange={(e) => setFormData({ ...formData, product: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  {complaintCategories.filter(c => c !== 'All Products').map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Intake Channel</label>
                <select
                  value={formData.channel}
                  onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  <option value="Branch">Branch</option>
                  <option value="Phone">Phone Rep</option>
                  <option value="Mobile App">Mobile Banking App</option>
                  <option value="CFPB Portal">CFPB Government Portal</option>
                  <option value="Executive Email">Executive Escalation</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Disputed Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={formData.disputedAmount}
                  onChange={(e) => setFormData({ ...formData, disputedAmount: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl font-mono text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Priority</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  {complaintPriorities.filter(p => p !== 'All Priorities').map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Regulatory Standard</label>
                <select
                  value={formData.regulatoryTag}
                  onChange={(e) => setFormData({ ...formData, regulatoryTag: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  <option value="None">None (Standard Dispute)</option>
                  <option value="Regulation E (10-day provisional credit)">Regulation E (EFT)</option>
                  <option value="Regulation Z (Truth in Lending)">Regulation Z (Card Dispute)</option>
                  <option value="CFPB Expedited">CFPB Expedited (15-Day)</option>
                  <option value="FCRA (Fair Credit Reporting Act)">FCRA (Credit Bureau)</option>
                  <option value="RESPA (Real Estate Settlement)">RESPA (Escrow/Mortgage)</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Target SLA Days</label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={formData.slaDays}
                  onChange={(e) => setFormData({ ...formData, slaDays: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>

            <div>
              <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Full Customer Complaint Narrative *</label>
              <textarea
                required
                rows={4}
                placeholder="Detailed statement of customer complaint, transaction timestamps, evidence provided, and desired outcome..."
                value={formData.narrative}
                onChange={(e) => setFormData({ ...formData, narrative: e.target.value })}
                className="w-full p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 leading-relaxed"
              />
            </div>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button
              type="button"
              onClick={() => setIsNewModalOpen(false)}
              className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-bold rounded-xl shadow-md shadow-blue-500/30 transition-all flex items-center gap-1.5"
            >
              <PlusCircle className="h-4 w-4" />
              <span>Submit & Create Case</span>
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};
