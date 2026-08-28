import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockComplaintsData, mockAgents } from '../data/mockComplaints';

const WorkbenchContext = createContext();

export const WorkbenchProvider = ({ children }) => {
  const [complaints, setComplaints] = useState(() => {
    const saved = localStorage.getItem('apex_bank_complaints_v1');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Failed to parse saved complaints", e);
      }
    }
    return mockComplaintsData;
  });

  const [selectedComplaintId, setSelectedComplaintId] = useState(mockComplaintsData[0]?.id || null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('All Products');
  const [selectedStatus, setSelectedStatus] = useState('All Statuses');
  const [selectedPriority, setSelectedPriority] = useState('All Priorities');
  const [activeTab, setActiveTab] = useState('queue'); // 'queue' | 'analytics' | 'compliance'
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(mockAgents[0].name);
  const [toasts, setToasts] = useState([]);
  
  const [darkMode, setDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('apex_theme');
    if (savedTheme) return savedTheme === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    localStorage.setItem('apex_bank_complaints_v1', JSON.stringify(complaints));
  }, [complaints]);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('apex_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('apex_theme', 'light');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(prev => !prev);

  const showToast = (title, message, type = 'info') => {
    const id = Date.now().toString() + Math.random().toString();
    setToasts(prev => [...prev, { id, title, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4500);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const selectedComplaint = complaints.find(c => c.id === selectedComplaintId) || null;

  const addComplaint = (complaintData) => {
    const newId = `CMP-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    const newRecord = {
      ...complaintData,
      id: newId,
      createdAt: new Date().toISOString(),
      status: complaintData.status || 'New',
      timeline: [
        {
          id: `ev-${Date.now()}`,
          timestamp: new Date().toISOString(),
          type: 'complaint_filed',
          author: `${currentAgent} (Intake)`,
          content: `Complaint logged directly into Resolution Workbench: ${complaintData.title}`
        }
      ]
    };

    setComplaints(prev => [newRecord, ...prev]);
    setSelectedComplaintId(newId);
    showToast('Complaint Logged', `Case #${newId} created successfully.`, 'success');
  };

  const updateComplaintStatus = (id, newStatus, reason = '') => {
    setComplaints(prev => prev.map(comp => {
      if (comp.id !== id) return comp;
      const updatedTimeline = [
        ...comp.timeline,
        {
          id: `ev-${Date.now()}`,
          timestamp: new Date().toISOString(),
          type: 'agent_note',
          author: currentAgent,
          content: `Status changed from ${comp.status} to ${newStatus}.${reason ? ` Reason: ${reason}` : ''}`
        }
      ];
      return {
        ...comp,
        status: newStatus,
        timeline: updatedTimeline
      };
    }));
    showToast('Status Updated', `Case ${id} moved to ${newStatus}.`, 'info');
  };

  const assignComplaint = (id, agentName) => {
    setComplaints(prev => prev.map(comp => {
      if (comp.id !== id) return comp;
      return {
        ...comp,
        assignedTo: agentName,
        timeline: [
          ...comp.timeline,
          {
            id: `ev-${Date.now()}`,
            timestamp: new Date().toISOString(),
            type: 'agent_note',
            author: currentAgent,
            content: `Reassigned case to ${agentName}.`
          }
        ]
      };
    }));
    showToast('Assignment Updated', `Case ${id} assigned to ${agentName}.`, 'info');
  };

  const addTimelineNote = (id, noteText, noteType = 'agent_note') => {
    if (!noteText.trim()) return;
    setComplaints(prev => prev.map(comp => {
      if (comp.id !== id) return comp;
      return {
        ...comp,
        timeline: [
          ...comp.timeline,
          {
            id: `ev-${Date.now()}`,
            timestamp: new Date().toISOString(),
            type: noteType,
            author: currentAgent,
            content: noteText.trim()
          }
        ]
      };
    }));
    showToast('Note Added', `Internal note appended to ${id}.`, 'success');
  };

  const issueRemediation = (id, remediationData) => {
    setComplaints(prev => prev.map(comp => {
      if (comp.id !== id) return comp;
      return {
        ...comp,
        recommendedRemediation: remediationData,
        timeline: [
          ...comp.timeline,
          {
            id: `ev-${Date.now()}`,
            timestamp: new Date().toISOString(),
            type: 'system_event',
            author: `${currentAgent} (Remediation Authority)`,
            content: `Financial / Policy Remediation Executed: ${remediationData.action} - Amount: $${Number(remediationData.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}. Policy Reference: ${remediationData.regulationBasis}`
          }
        ]
      };
    }));
    showToast('Remediation Executed', `Financial/Policy remediation logged for ${id}.`, 'success');
  };

  const resolveComplaint = (id, resolutionSummary, refundAmount = 0) => {
    setComplaints(prev => prev.map(comp => {
      if (comp.id !== id) return comp;
      return {
        ...comp,
        status: 'Resolved',
        timeline: [
          ...comp.timeline,
          {
            id: `ev-${Date.now()}`,
            timestamp: new Date().toISOString(),
            type: 'agent_note',
            author: currentAgent,
            content: `CASE RESOLVED. Summary: ${resolutionSummary}. Settlement / Refund: $${Number(refundAmount).toFixed(2)}.`
          }
        ]
      };
    }));
    showToast('Case Resolved', `Complaint ${id} has been successfully closed.`, 'success');
  };

  const resetToSampleData = () => {
    setComplaints(mockComplaintsData);
    setSelectedComplaintId(mockComplaintsData[0]?.id);
    localStorage.removeItem('apex_bank_complaints_v1');
    showToast('Reset Complete', 'Loaded default banking complaints data.', 'info');
  };

  const exportToCsv = () => {
    const headers = ["ID", "Customer Name", "Account Number", "Tier", "Product", "Priority", "Status", "Disputed Amount", "Regulatory Tag", "Assigned To", "Created At"];
    const rows = complaints.map(c => [
      c.id,
      `"${c.customerName}"`,
      c.accountNumber,
      c.customerTier,
      c.product,
      c.priority,
      c.status,
      c.disputedAmount,
      `"${c.regulatoryTag}"`,
      `"${c.assignedTo}"`,
      c.createdAt
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `apex_bank_complaints_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Export Successful', 'Downloaded complaint records as CSV.', 'success');
  };

  // Filtered complaints computation
  const filteredComplaints = complaints.filter(comp => {
    const matchesSearch = searchQuery === '' || 
      comp.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.accountNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.narrative.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesProduct = selectedProduct === 'All Products' || comp.product === selectedProduct;
    const matchesStatus = selectedStatus === 'All Statuses' || comp.status === selectedStatus;
    const matchesPriority = selectedPriority === 'All Priorities' || comp.priority === selectedPriority;

    return matchesSearch && matchesProduct && matchesStatus && matchesPriority;
  });

  return (
    <WorkbenchContext.Provider value={{
      complaints,
      filteredComplaints,
      selectedComplaintId,
      setSelectedComplaintId,
      selectedComplaint,
      searchQuery,
      setSearchQuery,
      selectedProduct,
      setSelectedProduct,
      selectedStatus,
      setSelectedStatus,
      selectedPriority,
      setSelectedPriority,
      activeTab,
      setActiveTab,
      isNewModalOpen,
      setIsNewModalOpen,
      currentAgent,
      setCurrentAgent,
      darkMode,
      toggleDarkMode,
      toasts,
      showToast,
      removeToast,
      addComplaint,
      updateComplaintStatus,
      assignComplaint,
      addTimelineNote,
      issueRemediation,
      resolveComplaint,
      resetToSampleData,
      exportToCsv
    }}>
      {children}
    </WorkbenchContext.Provider>
  );
};

export const useWorkbench = () => {
  const context = useContext(WorkbenchContext);
  if (!context) {
    throw new Error('useWorkbench must be used within a WorkbenchProvider');
  }
  return context;
};
