import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  User, 
  History, 
  FileText,
  AlertTriangle,
  PlusCircle,
  X,
  UserCheck,
  Briefcase,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import './App.css';

// Interface definitions based on the backend schema
interface ActivityLog {
  id: number;
  complaint_id: number;
  action: string;
  performed_by: string;
  comments?: string;
  timestamp: string;
}

interface Complaint {
  id: number;
  customer_name: string;
  account_number: string;
  account_type: string;
  severity: string;
  status: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
}

function App() {
  const [activeRole, setActiveRole] = useState('Intake Specialist');
  const [currentView, setCurrentView] = useState('dashboard');
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Details Drawer State
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);

  // Offline mock logs registry (to persist transition history when backend is not running)
  const [localLogs, setLocalLogs] = useState<Record<number, ActivityLog[]>>({});

  // Helper to construct mock initial logs for seeded complaints
  const getInitialLogs = (complaintId: number, createdAt: string): ActivityLog[] => {
    return [
      {
        id: complaintId * 1000,
        complaint_id: complaintId,
        action: "Created",
        performed_by: "System",
        comments: "Complaint registered during system initialization.",
        timestamp: createdAt
      }
    ];
  };

  // Fetch complaints from backend
  const fetchComplaints = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/api/complaints');
      setComplaints(response.data);
    } catch (err: any) {
      console.warn('Backend connection failed, using offline seeded fallback:', err.message);
      // Fallback if backend is offline
      if (complaints.length === 0) {
        const offlineFallbacks: Complaint[] = [
          {
            id: 1,
            customer_name: "John Doe",
            account_number: "XXXXXX4321",
            account_type: "Checking",
            severity: "High",
            status: "New",
            created_at: new Date(Date.now() - 3600000 * 2).toISOString(), // 2 hours ago
            updated_at: new Date(Date.now() - 3600000 * 2).toISOString()
          },
          {
            id: 2,
            customer_name: "Jane Smith",
            account_number: "XXXXXX8765",
            account_type: "Savings",
            severity: "Medium",
            status: "New",
            created_at: new Date(Date.now() - 3600000 * 5).toISOString(), // 5 hours ago
            updated_at: new Date(Date.now() - 3600000 * 5).toISOString()
          },
          {
            id: 3,
            customer_name: "Robert Johnson",
            account_number: "XXXXXX2468",
            account_type: "Credit Card",
            severity: "Low",
            status: "New",
            created_at: new Date(Date.now() - 3600000 * 24).toISOString(), // 1 day ago
            updated_at: new Date(Date.now() - 3600000 * 24).toISOString()
          },
          {
            id: 4,
            customer_name: "Emily Davis",
            account_number: "XXXXXX1357",
            account_type: "Credit Card",
            severity: "High",
            status: "New",
            created_at: new Date(Date.now() - 3600000 * 48).toISOString(), // 2 days ago
            updated_at: new Date(Date.now() - 3600000 * 48).toISOString()
          }
        ];
        setComplaints(offlineFallbacks);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  // Fetch full details & activity logs for a complaint
  const handleOpenDrawer = async (complaint: Complaint) => {
    setSelectedComplaint(complaint);
    setLoadingLogs(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/complaints/${complaint.id}`);
      setActivityLogs(response.data.activity_logs);
    } catch (err: any) {
      console.warn('Backend connection failed, loading offline timeline:', err.message);
      // Fallback to offline timeline logs
      const seededLogs = getInitialLogs(complaint.id, complaint.created_at);
      const transitions = localLogs[complaint.id] || [];
      setActivityLogs([...seededLogs, ...transitions]);
    } finally {
      setLoadingLogs(false);
    }
  };

  // Close the Slide-out details drawer
  const handleCloseDrawer = () => {
    setSelectedComplaint(null);
    setActivityLogs([]);
  };

  // Perform state transition
  const handleTransition = async (complaintId: number, currentStatus: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Avoid opening the drawer when clicking the transition button
    
    // Map current status to next status and action details
    let nextStatus = '';
    let actionName = '';
    let comment = '';
    
    if (currentStatus === 'New') {
      nextStatus = 'Assigned';
      actionName = 'Assigned Specialist';
      comment = `Assigned to Specialist by ${activeRole}.`;
    } else if (currentStatus === 'Assigned') {
      nextStatus = 'In Progress';
      actionName = 'Started Investigation';
      comment = `Investigation started by ${activeRole}.`;
    } else if (currentStatus === 'In Progress') {
      nextStatus = 'Resolved';
      actionName = 'Resolved Case';
      comment = `Complaint resolved and closed by ${activeRole}.`;
    } else {
      return; // Invalid transition
    }

    try {
      // Make backend POST request
      const response = await axios.post(`http://localhost:8000/api/complaints/${complaintId}/transition`, {
        new_status: nextStatus,
        performed_by: activeRole,
        comments: comment
      });
      
      // Update local state with updated complaint returned from backend
      setComplaints(prev => prev.map(c => c.id === complaintId ? response.data : c));
      
      // If the drawer is currently open for this complaint, refresh logs
      if (selectedComplaint && selectedComplaint.id === complaintId) {
        handleOpenDrawer(response.data);
      }
    } catch (err: any) {
      console.warn('Backend connection failed, performing offline mock transition:', err.message);
      
      // Offline fallback: Update state locally
      setComplaints(prev => prev.map(c => {
        if (c.id === complaintId) {
          const updated = {
            ...c,
            status: nextStatus,
            assigned_to: nextStatus === 'Assigned' ? (activeRole === 'Intake Specialist' ? 'Specialist Cooper' : activeRole) : c.assigned_to,
            updated_at: new Date().toISOString()
          };
          
          // Generate local log entry
          const newLocalLog: ActivityLog = {
            id: Date.now(),
            complaint_id: complaintId,
            action: actionName,
            performed_by: activeRole,
            comments: comment,
            timestamp: new Date().toISOString()
          };
          
          // Append log to local logs registry
          setLocalLogs(prevLogs => {
            const list = prevLogs[complaintId] || [];
            return {
              ...prevLogs,
              [complaintId]: [...list, newLocalLog]
            };
          });

          // Refresh drawer logs if open
          if (selectedComplaint && selectedComplaint.id === complaintId) {
            const baseLogs = getInitialLogs(complaintId, c.created_at);
            setActivityLogs([...baseLogs, ...(localLogs[complaintId] || []), newLocalLog]);
            setSelectedComplaint(updated);
          }
          
          return updated;
        }
        return c;
      }));
    }
  };

  // Compute metrics dynamically from state
  const totalComplaints = complaints.length;
  const newComplaints = complaints.filter(c => c.status === 'New').length;
  const inProgressComplaints = complaints.filter(c => c.status === 'In Progress' || c.status === 'Assigned').length;
  const resolvedComplaints = complaints.filter(c => c.status === 'Resolved').length;

  // Kanban statuses column mapping
  const statuses = ['New', 'Assigned', 'In Progress', 'Resolved'];

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">
            <ShieldAlert size={22} />
          </div>
          <span className="logo-text">Aegis Portal</span>
        </div>
        
        <nav className="sidebar-menu">
          <button 
            className={`menu-item ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            <LayoutDashboard size={18} className="menu-icon" />
            Dashboard
          </button>
          
          <button 
            className={`menu-item ${currentView === 'new-complaint' ? 'active' : ''}`}
            onClick={() => setCurrentView('new-complaint')}
          >
            <PlusCircle size={18} className="menu-icon" />
            Register Complaint
          </button>

          <button 
            className={`menu-item ${currentView === 'audit-logs' ? 'active' : ''}`}
            onClick={() => setCurrentView('audit-logs')}
          >
            <History size={18} className="menu-icon" />
            Audit History
          </button>
        </nav>
        
        <div className="sidebar-footer">
          Banking MVP v1.0
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Header */}
        <header className="header">
          <h1 className="header-title">Banking Internal Complaint Tracker</h1>
          
          <div className="role-switcher">
            <label htmlFor="role-select" className="role-label">Active Role:</label>
            <select 
              id="role-select"
              className="role-select" 
              value={activeRole} 
              onChange={(e) => setActiveRole(e.target.value)}
            >
              <option value="Intake Specialist">Intake Specialist</option>
              <option value="Investigator">Investigator</option>
            </select>
          </div>
        </header>

        {/* Dynamic Views */}
        {currentView === 'dashboard' && (
          <div className="dashboard-view">
            <div className="dashboard-hero">
              <h2 className="hero-title">Overview Dashboard</h2>
              <p className="hero-subtitle">
                Welcome back, <strong>{activeRole}</strong>. Monitor and manage complaints in real-time.
              </p>
            </div>

            {/* Metrics Overview Grid */}
            <section className="metrics-grid">
              <div className="metric-card">
                <div className="metric-info">
                  <span className="metric-label">Total Complaints</span>
                  <span className="metric-value">{totalComplaints}</span>
                </div>
                <div className="metric-icon-wrapper">
                  <FileText size={24} />
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-info">
                  <span className="metric-label">New Complaints</span>
                  <span className="metric-value">{newComplaints}</span>
                </div>
                <div className="metric-icon-wrapper" style={{ backgroundColor: '#eff6ff', color: '#3b82f6', borderColor: '#bfdbfe' }}>
                  <AlertTriangle size={24} />
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-info">
                  <span className="metric-label">Under Investigation</span>
                  <span className="metric-value">{inProgressComplaints}</span>
                </div>
                <div className="metric-icon-wrapper" style={{ backgroundColor: '#fffbeb', color: '#d97706', borderColor: '#fef3c7' }}>
                  <Clock size={24} />
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-info">
                  <span className="metric-label">Resolved Cases</span>
                  <span className="metric-value">{resolvedComplaints}</span>
                </div>
                <div className="metric-icon-wrapper" style={{ backgroundColor: '#ecfdf5', color: '#10b981', borderColor: '#a7f3d0' }}>
                  <CheckCircle2 size={24} />
                </div>
              </div>
            </section>

            {/* Interactive Kanban Board */}
            <section className="kanban-board">
              {statuses.map(status => {
                const filtered = complaints.filter(c => c.status === status);
                
                // Set appropriate display header for New column as required by tests
                const columnDisplayTitle = status === 'New' ? 'New Queue' : status;

                return (
                  <div 
                    key={status} 
                    className="kanban-column" 
                    data-testid={`column-${status}`}
                  >
                    <div className="column-header">
                      <h3 className="column-title">{columnDisplayTitle}</h3>
                      <span className="column-count">{filtered.length}</span>
                    </div>

                    <div className="cards-container">
                      {filtered.map(complaint => (
                        <div 
                          key={complaint.id} 
                          className="complaint-card"
                          onClick={() => handleOpenDrawer(complaint)}
                        >
                          <div className="card-header">
                            <h4 className="card-customer">{complaint.customer_name}</h4>
                            <span className={`severity-badge severity-${complaint.severity.toLowerCase()}`}>
                              {complaint.severity}
                            </span>
                          </div>

                          <p className="card-description">{complaint.description}</p>

                          <div className="card-meta">
                            <span className="card-meta-item">
                              <FileText size={12} />
                              {complaint.account_type}
                            </span>
                            <span className="card-meta-item">
                              <User size={12} />
                              {complaint.assigned_to ? complaint.assigned_to : 'Unassigned'}
                            </span>
                          </div>

                          {/* Context-aware state transition button */}
                          {status !== 'Resolved' && (
                            <div className="card-actions">
                              {status === 'New' && (
                                <button 
                                  className="card-btn"
                                  disabled={activeRole !== 'Intake Specialist'}
                                  onClick={(e) => handleTransition(complaint.id, status, e)}
                                >
                                  <UserCheck size={14} />
                                  Assign
                                </button>
                              )}

                              {status === 'Assigned' && (
                                <button 
                                  className="card-btn"
                                  disabled={activeRole !== 'Investigator'}
                                  onClick={(e) => handleTransition(complaint.id, status, e)}
                                  style={{ backgroundColor: '#fffbeb', color: '#d97706' }}
                                >
                                  <Briefcase size={14} />
                                  Investigate
                                </button>
                              )}

                              {status === 'In Progress' && (
                                <button 
                                  className="card-btn"
                                  disabled={activeRole !== 'Investigator'}
                                  onClick={(e) => handleTransition(complaint.id, status, e)}
                                  style={{ backgroundColor: '#ecfdf5', color: '#10b981' }}
                                >
                                  <CheckCircle2 size={14} />
                                  Resolve
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      ))}

                      {filtered.length === 0 && (
                        <div style={{ color: '#9ca3af', fontSize: '0.85rem', textAlign: 'center', padding: '24px 0' }}>
                          No cards in column
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </section>
          </div>
        )}

        {currentView === 'new-complaint' && (
          <div className="dashboard-view">
            <div className="content-placeholder">
              <h3>Complaint Intake Form</h3>
              <p>Form to register a new customer complaint will render here.</p>
            </div>
          </div>
        )}

        {currentView === 'audit-logs' && (
          <div className="dashboard-view">
            <div className="content-placeholder">
              <h3>Audit Logging Timeline</h3>
              <p>State transition timelines and audit log records will render here.</p>
            </div>
          </div>
        )}
      </main>

      {/* Slide-out Complaint Details Drawer */}
      {selectedComplaint && (
        <div className="drawer-backdrop" onClick={handleCloseDrawer}>
          <div className="drawer" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div className="drawer-title-wrapper">
                <ShieldAlert size={20} className="metric-icon" />
                <h3 className="drawer-title">Complaint Details</h3>
              </div>
              <button className="drawer-close" onClick={handleCloseDrawer}>
                <X size={20} />
              </button>
            </div>

            <div className="drawer-body">
              <div className="drawer-section">
                <span className="section-label">Customer Information</span>
                <div className="drawer-field-grid">
                  <div className="drawer-field">
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Customer Name</span>
                    <div className="field-value">{selectedComplaint.customer_name}</div>
                  </div>
                  <div className="drawer-field">
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Account Number</span>
                    <div className="field-value">{selectedComplaint.account_number}</div>
                  </div>
                </div>
              </div>

              <div className="drawer-section">
                <span className="section-label">Account & Severity</span>
                <div className="drawer-field-grid">
                  <div className="drawer-field">
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Account Type</span>
                    <div className="field-value">{selectedComplaint.account_type}</div>
                  </div>
                  <div className="drawer-field">
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Severity Level</span>
                    <div style={{ marginTop: '4px' }}>
                      <span className={`severity-badge severity-${selectedComplaint.severity.toLowerCase()}`}>
                        {selectedComplaint.severity}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="drawer-section">
                <span className="section-label">Workflow Details</span>
                <div className="drawer-field-grid">
                  <div className="drawer-field">
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Current Status</span>
                    <div className="field-value">{selectedComplaint.status}</div>
                  </div>
                  <div className="drawer-field">
                    <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Assigned Specialist</span>
                    <div className="field-value">{selectedComplaint.assigned_to || 'Unassigned'}</div>
                  </div>
                </div>
              </div>

              <div className="drawer-section">
                <span className="section-label">Complaint Description</span>
                <div className="drawer-field-full">
                  {selectedComplaint.description}
                </div>
              </div>

              {/* Activity Log Timeline */}
              <div className="drawer-section">
                <span className="section-label">Activity Log Timeline</span>
                {loadingLogs ? (
                  <div style={{ color: '#6b7280', fontSize: '0.85rem' }}>Loading timeline events...</div>
                ) : (
                  <div className="timeline">
                    {activityLogs.map(log => (
                      <div key={log.id} className="timeline-item">
                        <div className="timeline-dot"></div>
                        <div className="timeline-header">
                          <span className="timeline-action">{log.action}</span>
                          <span className="timeline-time">
                            {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <div className="timeline-by">Performed by: {log.performed_by}</div>
                        {log.comments && <div className="timeline-comments">{log.comments}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
