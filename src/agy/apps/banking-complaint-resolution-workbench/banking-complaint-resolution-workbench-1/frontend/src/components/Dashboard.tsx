import React, { useState, useEffect } from 'react';
import { useRole } from '../context/RoleContext';

export interface AuditLog {
  id: number;
  timestamp: string;
  user_name: string;
  user_role: string;
  event_type: string;
  description: string;
}

export interface Complaint {
  id: string;
  customer_name: string;
  account_number: string;
  customer_email: string;
  customer_phone: string;
  title: string;
  description: string;
  category: string;
  subcategory: string;
  disputed_amount: number;
  priority: string;
  status: string;
  sla_deadline: string;
  assigned_to: string | null;
  logged_by: string | null;
  resolution_notes: string | null;
  supervisor_feedback: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComplaintDetails extends Complaint {
  audit_logs: AuditLog[];
}

export interface Stats {
  active_cases: number;
  pending_approval: number;
  sla_critical: number;
  resolved_cases: number;
}

export interface ToastMessage {
  text: string;
  type: 'success' | 'error';
}

const CATEGORIES = [
  'Credit Cards',
  'Digital Banking',
  'Mortgages',
  'Savings Accounts',
  'Personal Loans'
];

const SUBCATEGORIES = [
  'Fee Dispute',
  'Unauthorised Charge',
  'Service Delay',
  'Interest Dispute',
  'Other'
];

const Dashboard: React.FC = () => {
  const { activeUser, fetchWithAuth } = useRole();

  // State Management
  const [stats, setStats] = useState<Stats | null>(null);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [selectedComplaintId, setSelectedComplaintId] = useState<string | null>(null);
  const [selectedDetails, setSelectedComplaintDetails] = useState<ComplaintDetails | null>(null);
  const [loadingStats, setLoadingStats] = useState<boolean>(true);
  const [loadingComplaints, setLoadingComplaints] = useState<boolean>(true);
  const [loadingDetails, setLoadingDetails] = useState<boolean>(false);
  const [toast, setToast] = useState<ToastMessage | null>(null);

  // Filters & Search
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');

  // Log Complaint Modal Form State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [customerName, setCustomerName] = useState<string>('');
  const [accountNumber, setAccountNumber] = useState<string>('');
  const [customerEmail, setCustomerEmail] = useState<string>('');
  const [customerPhone, setCustomerPhone] = useState<string>('');
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [category, setCategory] = useState<string>(CATEGORIES[0]);
  const [subcategory, setSubcategory] = useState<string>(SUBCATEGORIES[0]);
  const [disputedAmount, setDisputedAmount] = useState<string>('0.00');
  const [priority, setPriority] = useState<string>('Medium');

  // New Case Action States
  const [commentText, setCommentText] = useState<string>('');
  const [isProposalModalOpen, setIsProposalModalOpen] = useState<boolean>(false);
  const [resolutionNotes, setResolutionNotes] = useState<string>('');
  const [isRejectModalOpen, setIsRejectModalOpen] = useState<boolean>(false);
  const [rejectionFeedback, setRejectionFeedback] = useState<string>('');

  // Trigger toast alert helper
  const showToast = (text: string, type: 'success' | 'error') => {
    setToast({ text, type });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  // Fetch Stats from API
  const loadStats = async () => {
    try {
      setLoadingStats(true);
      const res = await fetchWithAuth('/api/dashboard/stats');
      if (res.ok) {
        const data = await res.json() as Stats;
        setStats(data);
      } else {
        showToast('Failed to load dashboard metrics', 'error');
      }
    } catch {
      showToast('Error connecting to backend API', 'error');
    } finally {
      setLoadingStats(false);
    }
  };

  // Fetch Complaints list
  const loadComplaints = async () => {
    try {
      setLoadingComplaints(true);
      let url = '/api/complaints';
      const params: string[] = [];
      if (statusFilter) {
        params.push(`status=${encodeURIComponent(statusFilter)}`);
      }
      if (params.length > 0) {
        url += `?${params.join('&')}`;
      }
      const res = await fetchWithAuth(url);
      if (res.ok) {
        const data = await res.json() as Complaint[];
        setComplaints(data);
      } else {
        showToast('Failed to retrieve complaints data', 'error');
      }
    } catch {
      showToast('Error connecting to backend API', 'error');
    } finally {
      setLoadingComplaints(false);
    }
  };

  // Fetch Complaint Details by ID
  const loadComplaintDetails = async (id: string) => {
    try {
      setLoadingDetails(true);
      const res = await fetchWithAuth(`/api/complaints/${id}`);
      if (res.ok) {
        const data = await res.json() as ComplaintDetails;
        setSelectedComplaintDetails(data);
      } else {
        showToast(`Failed to load case details for ${id}`, 'error');
      }
    } catch {
      showToast('Error fetching details from server', 'error');
    } finally {
      setLoadingDetails(false);
    }
  };

  // Initial and reactive data loads
  useEffect(() => {
    loadStats();
    loadComplaints();
  }, [activeUser, statusFilter]);

  // Handle row selection
  const handleRowClick = (id: string) => {
    setSelectedComplaintId(id);
    loadComplaintDetails(id);
  };

  // Clear selected complaint
  const handleCloseDetails = () => {
    setSelectedComplaintId(null);
    setSelectedComplaintDetails(null);
  };

  // Handle Log Complaint Form Submission
  const handleLogComplaint = async (e: React.FormEvent) => {
    e.preventDefault();

    // Simple robust form validation
    if (!customerName.trim() || !accountNumber.trim() || !customerEmail.trim() || !customerPhone.trim() || !title.trim() || !description.trim()) {
      showToast('Please fill out all required fields.', 'error');
      return;
    }

    const disputedVal = parseFloat(disputedAmount);
    if (isNaN(disputedVal) || disputedVal < 0) {
      showToast('Disputed amount must be a non-negative number.', 'error');
      return;
    }

    const payload = {
      customer_name: customerName.trim(),
      account_number: accountNumber.trim(),
      customer_email: customerEmail.trim(),
      customer_phone: customerPhone.trim(),
      title: title.trim(),
      description: description.trim(),
      category,
      subcategory,
      disputed_amount: disputedVal,
      priority,
    };

    try {
      const res = await fetchWithAuth('/api/complaints', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        showToast('Complaint logged successfully!', 'success');
        setIsModalOpen(false);
        // Reset fields
        setCustomerName('');
        setAccountNumber('');
        setCustomerEmail('');
        setCustomerPhone('');
        setTitle('');
        setDescription('');
        setCategory(CATEGORIES[0]);
        setSubcategory(SUBCATEGORIES[0]);
        setDisputedAmount('0.00');
        setPriority('Medium');

        // Re-fetch list and statistics
        loadStats();
        loadComplaints();
      } else {
        const errData = await res.json() as { detail?: string };
        showToast(errData.detail || 'Failed to submit complaint', 'error');
      }
    } catch {
      showToast('Error posting to backend API', 'error');
    }
  };

  // Claim Case API Call
  const handleClaimCase = async () => {
    if (!selectedComplaintId) return;
    try {
      const res = await fetchWithAuth(`/api/complaints/${selectedComplaintId}/claim`, {
        method: 'POST',
      });
      if (res.ok) {
        showToast('Case claimed successfully!', 'success');
        await loadStats();
        await loadComplaints();
        await loadComplaintDetails(selectedComplaintId);
      } else {
        const errData = await res.json() as { detail?: string };
        showToast(errData.detail || 'Failed to claim case', 'error');
      }
    } catch {
      showToast('Error connecting to backend API', 'error');
    }
  };

  // Add Comment API Call
  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedComplaintId) return;
    if (!commentText.trim()) {
      showToast('Comment cannot be empty.', 'error');
      return;
    }
    try {
      const res = await fetchWithAuth(`/api/complaints/${selectedComplaintId}/comment`, {
        method: 'POST',
        body: JSON.stringify({ comment: commentText.trim() }),
      });
      if (res.ok) {
        showToast('Comment added successfully!', 'success');
        setCommentText('');
        await loadComplaintDetails(selectedComplaintId);
      } else {
        const errData = await res.json() as { detail?: string };
        showToast(errData.detail || 'Failed to add comment', 'error');
      }
    } catch {
      showToast('Error connecting to backend API', 'error');
    }
  };

  // Submit Proposal API Call
  const handleProposeResolution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedComplaintId) return;
    if (!resolutionNotes.trim()) {
      showToast('Resolution notes cannot be empty.', 'error');
      return;
    }
    try {
      const res = await fetchWithAuth(`/api/complaints/${selectedComplaintId}/propose`, {
        method: 'POST',
        body: JSON.stringify({ resolution_notes: resolutionNotes.trim() }),
      });
      if (res.ok) {
        showToast('Resolution proposed successfully!', 'success');
        setIsProposalModalOpen(false);
        setResolutionNotes('');
        await loadStats();
        await loadComplaints();
        await loadComplaintDetails(selectedComplaintId);
      } else {
        const errData = await res.json() as { detail?: string };
        showToast(errData.detail || 'Failed to propose resolution', 'error');
      }
    } catch {
      showToast('Error connecting to backend API', 'error');
    }
  };

  // Approve Resolution API Call
  const handleApproveResolution = async () => {
    if (!selectedComplaintId) return;
    try {
      const res = await fetchWithAuth(`/api/complaints/${selectedComplaintId}/approve`, {
        method: 'POST',
      });
      if (res.ok) {
        showToast('Resolution approved and case closed successfully!', 'success');
        await loadStats();
        await loadComplaints();
        await loadComplaintDetails(selectedComplaintId);
      } else {
        const errData = await res.json() as { detail?: string };
        showToast(errData.detail || 'Failed to approve resolution', 'error');
      }
    } catch {
      showToast('Error connecting to backend API', 'error');
    }
  };

  // Reject / Request Revision API Call
  const handleRejectResolution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedComplaintId) return;
    if (!rejectionFeedback.trim()) {
      showToast('Feedback cannot be empty.', 'error');
      return;
    }
    try {
      const res = await fetchWithAuth(`/api/complaints/${selectedComplaintId}/reject`, {
        method: 'POST',
        body: JSON.stringify({ feedback: rejectionFeedback.trim() }),
      });
      if (res.ok) {
        showToast('Revision request submitted successfully!', 'success');
        setIsRejectModalOpen(false);
        setRejectionFeedback('');
        await loadStats();
        await loadComplaints();
        await loadComplaintDetails(selectedComplaintId);
      } else {
        const errData = await res.json() as { detail?: string };
        showToast(errData.detail || 'Failed to reject resolution', 'error');
      }
    } catch {
      showToast('Error connecting to backend API', 'error');
    }
  };

  // Compute SLA Countdown visual helpers
  const getSLACountdown = (slaDeadlineStr: string) => {
    const now = new Date();
    const deadline = new Date(slaDeadlineStr);
    const diffMs = deadline.getTime() - now.getTime();

    if (diffMs <= 0) {
      return { text: 'SLA Breached', type: 'critical' };
    }

    const diffHours = diffMs / (1000 * 60 * 60);
    if (diffHours < 24) {
      const hours = Math.floor(diffHours);
      const minutes = Math.floor((diffHours % 1) * 60);
      return { text: `${hours}h ${minutes}m left`, type: 'critical' };
    }

    const diffDays = Math.ceil(diffHours / 24);
    if (diffDays <= 3) {
      return { text: `${diffDays} days left`, type: 'warning' };
    }

    return { text: `${diffDays} days left`, type: 'normal' };
  };

  // Filter complaints based on Search Term and Category filter locally
  const filteredComplaints = complaints.filter((c: Complaint) => {
    const matchesSearch =
      c.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.title.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCategory = categoryFilter === '' || c.category === categoryFilter;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="dashboard-view">
      {/* Toast Alert Notifications */}
      {toast && (
        <div className={`toast-alert toast-${toast.type}`}>
          <div className="toast-icon">
            {toast.type === 'success' ? (
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
            )}
          </div>
          <div className="toast-text">{toast.text}</div>
        </div>
      )}

      {/* Page Title Row */}
      <div className="dashboard-header-row">
        <div>
          <h2 className="view-title">Complaint Dashboard</h2>
          <p className="view-subtitle">Real-time metrics, queue routing, and case verification hub.</p>
        </div>
        {activeUser.role === 'CSR' && (
          <button className="btn btn-primary btn-log-case" onClick={() => setIsModalOpen(true)}>
            <svg viewBox="0 0 24 24" width="16" height="16" className="btn-icon">
              <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
            </svg>
            Log New Complaint
          </button>
        )}
      </div>

      {/* Metric Widgets Grid */}
      <section className="metrics-grid">
        <div className="metric-card active-card">
          <div className="metric-header">
            <span className="metric-label">Active Cases</span>
            <div className="metric-icon active-icon">
              <svg viewBox="0 0 24 24" width="20" height="24">
                <path fill="currentColor" d="M19 3h-4.18C14.4 1.84 13.3 1 12 1s-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
              </svg>
            </div>
          </div>
          <div className="metric-value">
            {loadingStats ? <span className="metric-spinner">...</span> : stats?.active_cases}
          </div>
          <div className="metric-footer">Registered or investigating</div>
        </div>

        <div className="metric-card pending-card">
          <div className="metric-header">
            <span className="metric-label">Pending Approval</span>
            <div className="metric-icon pending-icon">
              <svg viewBox="0 0 24 24" width="20" height="24">
                <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
              </svg>
            </div>
          </div>
          <div className="metric-value">
            {loadingStats ? <span className="metric-spinner">...</span> : stats?.pending_approval}
          </div>
          <div className="metric-footer">Awaiting supervisor review</div>
        </div>

        <div className="metric-card critical-card">
          <div className="metric-header">
            <span className="metric-label">SLA Critical</span>
            <div className="metric-icon critical-icon">
              <svg viewBox="0 0 24 24" width="20" height="24">
                <path fill="currentColor" d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
            </div>
          </div>
          <div className="metric-value text-critical">
            {loadingStats ? <span className="metric-spinner">...</span> : stats?.sla_critical}
          </div>
          <div className="metric-footer alert-subtext">Less than 24 hours left</div>
        </div>

        <div className="metric-card resolved-card">
          <div className="metric-header">
            <span className="metric-label">Resolved Cases</span>
            <div className="metric-icon resolved-icon">
              <svg viewBox="0 0 24 24" width="20" height="24">
                <path fill="currentColor" d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z" />
              </svg>
            </div>
          </div>
          <div className="metric-value text-accent">
            {loadingStats ? <span className="metric-spinner">...</span> : stats?.resolved_cases}
          </div>
          <div className="metric-footer">Successfully closed</div>
        </div>
      </section>

      {/* Main Grid area with master-detail split screens */}
      <section className={`queue-section ${selectedComplaintId ? 'split-active' : ''}`}>
        {/* Left Side: Complaints Grid */}
        <div className="queue-list-container">
          {/* Table Filters Panel */}
          <div className="table-controls">
            <div className="search-box">
              <svg viewBox="0 0 24 24" width="16" height="16" className="search-icon">
                <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
              </svg>
              <input
                type="text"
                className="search-input"
                placeholder="Search Customer or Case ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="filter-group">
              <div className="select-wrapper">
                <select
                  className="filter-select"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="Registered">Registered</option>
                  <option value="Under Investigation">Under Investigation</option>
                  <option value="Resolution Proposed">Resolution Proposed</option>
                  <option value="Needs Revision">Needs Revision</option>
                  <option value="Resolved">Resolved</option>
                </select>
              </div>

              <div className="select-wrapper">
                <select
                  className="filter-select"
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <option value="">All Categories</option>
                  {CATEGORIES.map((cat: string) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Table Element */}
          <div className="table-responsive">
            {loadingComplaints ? (
              <div className="table-loading-state">
                <div className="loading-spinner"></div>
                <p>Retrieving complaints registry...</p>
              </div>
            ) : filteredComplaints.length === 0 ? (
              <div className="table-empty-state">
                <svg viewBox="0 0 24 24" width="48" height="48" className="empty-state-icon">
                  <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z" />
                </svg>
                <p className="empty-state-text">No complaints found matching the criteria.</p>
              </div>
            ) : (
              <table className="complaint-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Customer</th>
                    <th>Priority</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>SLA Countdown</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredComplaints.map((c: Complaint) => {
                    const sla = getSLACountdown(c.sla_deadline);
                    const isSelected = selectedComplaintId === c.id;
                    return (
                      <tr
                        key={c.id}
                        className={`complaint-row ${isSelected ? 'row-selected' : ''}`}
                        onClick={() => handleRowClick(c.id)}
                      >
                        <td className="col-id font-mono">{c.id}</td>
                        <td className="col-customer">
                          <div className="customer-name-cell">{c.customer_name}</div>
                          <div className="customer-account-sub font-mono">{c.account_number}</div>
                        </td>
                        <td className="col-priority">
                          <span className={`priority-badge prio-${c.priority.toLowerCase()}`}>
                            {c.priority}
                          </span>
                        </td>
                        <td className="col-category">{c.category}</td>
                        <td className="col-status">
                          <span className={`status-badge status-${c.status.toLowerCase().replace(' ', '-')}`}>
                            {c.status}
                          </span>
                        </td>
                        <td className="col-sla">
                          <span className={`sla-indicator sla-${sla.type}`}>
                            {sla.text}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
          <div className="table-footer-summary">
            Showing {filteredComplaints.length} of {complaints.length} logged complaints.
          </div>
        </div>

        {/* Right Side: Split Screen Details Panel */}
        {selectedComplaintId && (
          <div className="queue-detail-container">
            <div className="detail-panel-header">
              <div className="header-case-details">
                <span className="case-id-badge font-mono">{selectedComplaintId}</span>
                <span className="detail-status">
                  {selectedDetails && (
                    <span className={`status-badge status-${selectedDetails.status.toLowerCase().replace(' ', '-')}`}>
                      {selectedDetails.status}
                    </span>
                  )}
                </span>
              </div>
              <button className="btn-close-panel" onClick={handleCloseDetails} title="Close Panel">
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </button>
            </div>

            {loadingDetails ? (
              <div className="detail-loading-state">
                <div className="loading-spinner"></div>
                <p>Loading audit timeline...</p>
              </div>
            ) : selectedDetails ? (
              <div className="detail-panel-body">
                {/* Details Section */}
                <div className="detail-section">
                  <h3 className="detail-section-title">Customer Information</h3>
                  <div className="detail-grid">
                    <div className="detail-field">
                      <label className="field-label">Full Name</label>
                      <div className="field-value">{selectedDetails.customer_name}</div>
                    </div>
                    <div className="detail-field">
                      <label className="field-label">Account Number</label>
                      <div className="field-value font-mono">{selectedDetails.account_number}</div>
                    </div>
                    <div className="detail-field">
                      <label className="field-label">Email Address</label>
                      <div className="field-value">{selectedDetails.customer_email}</div>
                    </div>
                    <div className="detail-field">
                      <label className="field-label">Phone Number</label>
                      <div className="field-value">{selectedDetails.customer_phone}</div>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3 className="detail-section-title">Complaint Specifications</h3>
                  <div className="case-title-display">{selectedDetails.title}</div>
                  <div className="case-desc-display">{selectedDetails.description}</div>
                  
                  <div className="detail-grid gap-sm">
                    <div className="detail-field">
                      <label className="field-label">Category</label>
                      <div className="field-value">{selectedDetails.category} ({selectedDetails.subcategory})</div>
                    </div>
                    <div className="detail-field">
                      <label className="field-label">Disputed Amount</label>
                      <div className="field-value font-bold text-navy">
                        ${selectedDetails.disputed_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                    <div className="detail-field">
                      <label className="field-label">Priority Level</label>
                      <div className="field-value">
                        <span className={`priority-badge prio-${selectedDetails.priority.toLowerCase()}`}>
                          {selectedDetails.priority}
                        </span>
                      </div>
                    </div>
                    <div className="detail-field">
                      <label className="field-label">Assigned Handler</label>
                      <div className="field-value font-mono">
                        {selectedDetails.assigned_to ? `@${selectedDetails.assigned_to}` : 'Unassigned'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Supervisor Feedback / Resolution Proposed if applicable */}
                {selectedDetails.resolution_notes && (
                  <div className="detail-section detail-highlight accent-highlight">
                    <h3 className="detail-section-title text-accent">Proposed Resolution</h3>
                    <p className="highlight-text">{selectedDetails.resolution_notes}</p>
                  </div>
                )}

                {selectedDetails.supervisor_feedback && (
                  <div className="detail-section detail-highlight error-highlight">
                    <h3 className="detail-section-title text-critical">Supervisor Revision Feedback</h3>
                    <p className="highlight-text">{selectedDetails.supervisor_feedback}</p>
                  </div>
                )}

                {/* Case Actions Panel */}
                <div className="detail-section">
                  <h3 className="detail-section-title">Case Actions</h3>
                  <div className="detail-actions-panel">
                    {/* Claim Case Button (Case Handlers only, when status is Registered or Needs Revision) */}
                    {(selectedDetails.status === "Registered" || selectedDetails.status === "Needs Revision") && 
                     activeUser?.role === "Case Handler" && (
                      <button className="btn btn-primary btn-full" onClick={handleClaimCase}>
                        Claim Case & Start Investigation
                      </button>
                    )}

                    {/* Propose Resolution Button (Case Handlers only, when status is Under Investigation and assigned to current user) */}
                    {selectedDetails.status === "Under Investigation" && 
                     selectedDetails.assigned_to === activeUser?.username && (
                      <button className="btn btn-primary btn-full" onClick={() => setIsProposalModalOpen(true)}>
                        Propose Resolution
                      </button>
                    )}

                    {/* Supervisor Actions (Supervisors only, when status is Resolution Proposed) */}
                    {selectedDetails.status === "Resolution Proposed" && activeUser?.role === "Supervisor" && (
                      <div className="supervisor-action-buttons">
                        <button className="btn btn-primary btn-approve" onClick={handleApproveResolution}>
                          Approve & Resolve Case
                        </button>
                        <button className="btn btn-secondary btn-reject" onClick={() => setIsRejectModalOpen(true)}>
                          Request Revision (Reject)
                        </button>
                      </div>
                    )}

                    {/* Non-assignee info message */}
                    {selectedDetails.status === "Under Investigation" && 
                     selectedDetails.assigned_to !== activeUser?.username && (
                      <div className="info-message">
                        This case is currently being investigated by @{selectedDetails.assigned_to}.
                      </div>
                    )}

                    {/* Resolved indicator */}
                    {selectedDetails.status === "Resolved" && (
                      <div className="success-message">
                        This case is resolved and closed. No further actions are required.
                      </div>
                    )}
                    
                    {/* Fallback for CSR roles on existing cases */}
                    {activeUser?.role === "CSR" && (
                      <div className="info-message">
                        Customer Service Representatives have read-only access to active cases.
                      </div>
                    )}
                  </div>
                </div>

                {/* Audit Log Vertical Timeline */}
                <div className="detail-section">
                  <h3 className="detail-section-title">Audit Log & History Timeline</h3>
                  <div className="timeline-container">
                    {selectedDetails.audit_logs && selectedDetails.audit_logs.length > 0 ? (
                      selectedDetails.audit_logs.map((log: AuditLog) => (
                        <div key={log.id} className="timeline-item">
                          <div className="timeline-marker"></div>
                          <div className="timeline-content">
                            <div className="timeline-meta">
                              <span className="timeline-user">{log.user_name}</span>
                              <span className="timeline-user-role">({log.user_role})</span>
                              <span className="timeline-time">
                                {new Date(log.timestamp).toLocaleString()}
                              </span>
                            </div>
                            <div className="timeline-event-type font-mono">{log.event_type}</div>
                            <p className="timeline-desc">{log.description}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="no-timeline-text">No audit history found.</p>
                    )}
                  </div>

                  {/* Comment input form (Any Case Handler can add comments/notes to any case) */}
                  {activeUser?.role === "Case Handler" && (
                    <form onSubmit={handleAddComment} className="comment-form-container">
                      <input
                        type="text"
                        className="form-input comment-input"
                        placeholder="Type internal comment or timeline note..."
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        required
                      />
                      <button type="submit" className="btn btn-primary btn-comment">
                        Add Note
                      </button>
                    </form>
                  )}
                </div>
              </div>
            ) : null}
          </div>
        )}
      </section>

      {/* Log Complaint Overlay Modal (CSR Only) */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-container">
            <div className="modal-header">
              <div className="modal-header-title">
                <svg viewBox="0 0 24 24" width="22" height="22" className="text-accent modal-title-icon">
                  <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h10v2zm0-4H8v-2h10v2zm-3-5V3.5L18.5 9H13z" />
                </svg>
                Log New Customer Complaint
              </div>
              <button className="btn-close-modal" onClick={() => setIsModalOpen(false)}>
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleLogComplaint} className="modal-form">
              <div className="form-scrollable">
                <h4 className="form-section-header">Customer Identity & Account Details</h4>
                <div className="form-row">
                  <div className="form-field-group">
                    <label className="form-label required">Customer Full Name</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. Marcus Aurelius"
                      required
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                    />
                  </div>
                  <div className="form-field-group">
                    <label className="form-label required">Account Number</label>
                    <input
                      type="text"
                      className="form-input font-mono"
                      placeholder="e.g. ACT-98234-92"
                      required
                      value={accountNumber}
                      onChange={(e) => setAccountNumber(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-field-group">
                    <label className="form-label required">Email Address</label>
                    <input
                      type="email"
                      className="form-input"
                      placeholder="customer@email.com"
                      required
                      value={customerEmail}
                      onChange={(e) => setCustomerEmail(e.target.value)}
                    />
                  </div>
                  <div className="form-field-group">
                    <label className="form-label required">Phone Number</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="+1-555-0192"
                      required
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                    />
                  </div>
                </div>

                <h4 className="form-section-header margin-top-md">Dispute Specifications</h4>
                <div className="form-field-group">
                  <label className="form-label required">Complaint Title</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Short descriptive summary of the issue..."
                    required
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                </div>

                <div className="form-field-group">
                  <label className="form-label required">Complaint Narrative / Description</label>
                  <textarea
                    className="form-input form-textarea"
                    placeholder="Provide complete details about the customer's grievance, timeline, and requested resolution..."
                    required
                    rows={4}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>

                <div className="form-row">
                  <div className="form-field-group">
                    <label className="form-label required">Dispute Category</label>
                    <select
                      className="form-select"
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                    >
                      {CATEGORIES.map((cat: string) => (
                        <option key={cat} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-field-group">
                    <label className="form-label required">Subcategory</label>
                    <select
                      className="form-select"
                      value={subcategory}
                      onChange={(e) => setSubcategory(e.target.value)}
                    >
                      {SUBCATEGORIES.map((sub: string) => (
                        <option key={sub} value={sub}>
                          {sub}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-field-group">
                    <label className="form-label required">Disputed Amount ($)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      className="form-input font-mono"
                      required
                      value={disputedAmount}
                      onChange={(e) => setDisputedAmount(e.target.value)}
                    />
                  </div>
                  <div className="form-field-group">
                    <label className="form-label required">Initial Case Priority</label>
                    <select
                      className="form-select"
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                    >
                      <option value="Low">Low (15 days SLA)</option>
                      <option value="Medium">Medium (7 days SLA)</option>
                      <option value="High">High (3 days SLA)</option>
                      <option value="Critical">Critical (24 hours SLA)</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Log Complaint
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Propose Resolution Overlay Modal */}
      {isProposalModalOpen && (
        <div className="modal-overlay">
          <div className="modal-container">
            <div className="modal-header">
              <div className="modal-header-title">
                <svg viewBox="0 0 24 24" width="22" height="22" className="text-accent modal-title-icon">
                  <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h10v2zm0-4H8v-2h10v2zm-3-5V3.5L18.5 9H13z" />
                </svg>
                Propose Case Resolution
              </div>
              <button className="btn-close-modal" onClick={() => setIsProposalModalOpen(false)}>
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleProposeResolution} className="modal-form">
              <div className="form-scrollable">
                <label className="form-label required">Proposed Resolution Notes</label>
                <textarea
                  className="form-input form-textarea"
                  placeholder="Detail the actions taken to resolve the complaint, including any fee waivers, refunds, or customer communications..."
                  required
                  rows={6}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setIsProposalModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Submit Proposal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reject / Request Revision Overlay Modal */}
      {isRejectModalOpen && (
        <div className="modal-overlay">
          <div className="modal-container">
            <div className="modal-header">
              <div className="modal-header-title">
                <svg viewBox="0 0 24 24" width="22" height="22" className="text-critical modal-title-icon">
                  <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                </svg>
                Request Case Revision (Reject)
              </div>
              <button className="btn-close-modal" onClick={() => setIsRejectModalOpen(false)}>
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleRejectResolution} className="modal-form">
              <div className="form-scrollable">
                <label className="form-label required">Revision Feedback & Instructions</label>
                <textarea
                  className="form-input form-textarea"
                  placeholder="Specify what additional investigations or adjustments are required from the Case Handler..."
                  required
                  rows={6}
                  value={rejectionFeedback}
                  onChange={(e) => setRejectionFeedback(e.target.value)}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setIsRejectModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Submit Feedback
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export { Dashboard, CATEGORIES, SUBCATEGORIES };
