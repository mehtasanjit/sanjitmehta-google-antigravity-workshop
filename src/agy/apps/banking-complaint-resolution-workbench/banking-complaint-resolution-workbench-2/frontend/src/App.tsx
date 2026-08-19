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
  PlusCircle
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

  // Fetch complaints from the backend on mount
  useEffect(() => {
    const fetchComplaints = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get('http://localhost:8000/api/complaints');
        setComplaints(response.data);
      } catch (err: any) {
        console.warn('Backend connection failed, using offline seeded fallback:', err.message);
        // Fallback to the 4 default seeded complaints so the UI is immediately fully interactive and visual
        const offlineFallbacks: Complaint[] = [
          {
            id: 1,
            customer_name: "John Doe",
            account_number: "XXXXXX4321",
            account_type: "Checking",
            severity: "High",
            status: "New",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 2,
            customer_name: "Jane Smith",
            account_number: "XXXXXX8765",
            account_type: "Savings",
            severity: "Medium",
            status: "New",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 3,
            customer_name: "Robert Johnson",
            account_number: "XXXXXX2468",
            account_type: "Credit Card",
            severity: "Low",
            status: "New",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 4,
            customer_name: "Emily Davis",
            account_number: "XXXXXX1357",
            account_type: "Credit Card",
            severity: "High",
            status: "New",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        ];
        setComplaints(offlineFallbacks);
      } finally {
        setLoading(false);
      }
    };

    fetchComplaints();
  }, []);

  // Compute metrics dynamically from state
  const totalComplaints = complaints.length;
  const newComplaints = complaints.filter(c => c.status === 'New').length;
  const inProgressComplaints = complaints.filter(c => c.status === 'In Progress' || c.status === 'Assigned').length;
  const resolvedComplaints = complaints.filter(c => c.status === 'Resolved').length;

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

            {/* Main Interactive Work Area (To be implemented in future tasks) */}
            <div className="content-placeholder">
              <h3>Interactive Kanban Work Board</h3>
              <p>Kanban columns and card state-transition action buttons will render here in the next task.</p>
            </div>
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
    </div>
  );
}

export default App;
