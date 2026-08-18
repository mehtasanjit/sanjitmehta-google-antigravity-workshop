import React from 'react';
import { useRole, User } from '../context/RoleContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { activeUser, setActiveUser, users } = useRole();

  const handleUserChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = users.find((u: User) => u.username === event.target.value);
    if (selected) {
      setActiveUser(selected);
    }
  };

  return (
    <div className="app-container">
      {/* Persistent Header */}
      <header className="app-header">
        <div className="header-brand">
          <svg className="header-logo" viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
          <h1 className="header-title">Banking Complaint Resolution Workbench</h1>
          <span className="badge-mvp">MVP v1.0</span>
        </div>
        <div className="header-actions">
          <label htmlFor="user-switcher" className="switcher-label">Acting As:</label>
          <div className="switcher-wrapper">
            <select
              id="user-switcher"
              className="user-switcher"
              value={activeUser.username}
              onChange={handleUserChange}
            >
              {users.map((u: User) => (
                <option key={u.username} value={u.username}>
                  {u.name} ({u.role})
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <div className="app-body">
        {/* Sidebar */}
        <aside className="app-sidebar">
          {/* User Profile Card */}
          <div className="sidebar-profile">
            <div className="profile-avatar">
              {activeUser.name.split(' ').map((n: string) => n[0]).join('')}
            </div>
            <div className="profile-info">
              <div className="profile-name">{activeUser.name}</div>
              <div className="profile-username">@{activeUser.username}</div>
              <span className={`profile-role-badge role-${activeUser.role.toLowerCase().replace(' ', '-')}`}>
                {activeUser.role}
              </span>
            </div>
          </div>

          {/* Navigation Menu */}
          <nav className="sidebar-nav">
            <div className="nav-section-title">Navigation</div>
            <ul className="nav-list">
              <li className="nav-item active">
                <a href="#dashboard" className="nav-link">
                  <svg viewBox="0 0 24 24" width="16" height="16" className="nav-icon">
                    <path fill="currentColor" d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
                  </svg>
                  Complaint Dashboard
                </a>
              </li>
              <li className="nav-item disabled">
                <a href="#reports" className="nav-link">
                  <svg viewBox="0 0 24 24" width="16" height="16" className="nav-icon">
                    <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10H7v-2h10v2zm0-4H7V7h10v2zm0 8H7v-2h10v2z" />
                  </svg>
                  SLA Reports
                </a>
              </li>
              <li className="nav-item disabled">
                <a href="#audit" className="nav-link">
                  <svg viewBox="0 0 24 24" width="16" height="16" className="nav-icon">
                    <path fill="currentColor" d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" />
                  </svg>
                  System Audit Log
                </a>
              </li>
            </ul>
          </nav>

          {/* Quick SLA Help Info for Bank Staff */}
          <div className="sidebar-footer">
            <div className="sla-legend-title">SLA Priority Guide</div>
            <ul className="sla-legend-list">
              <li>
                <span className="dot dot-critical"></span>
                <strong>Critical</strong>: 24h Resolution
              </li>
              <li>
                <span className="dot dot-high"></span>
                <strong>High</strong>: 3 Days
              </li>
              <li>
                <span className="dot dot-medium"></span>
                <strong>Medium</strong>: 7 Days
              </li>
              <li>
                <span className="dot dot-low"></span>
                <strong>Low</strong>: 15 Days
              </li>
            </ul>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="app-main">
          <div className="main-content-wrapper">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export { Layout };
