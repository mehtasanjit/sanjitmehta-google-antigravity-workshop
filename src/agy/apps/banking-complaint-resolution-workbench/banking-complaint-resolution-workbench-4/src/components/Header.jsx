import React from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { mockAgents } from '../data/mockComplaints';
import { 
  Building2, 
  Search, 
  PlusCircle, 
  Download, 
  Moon, 
  Sun, 
  ShieldCheck, 
  BarChart3, 
  ListFilter,
  UserCheck,
  RotateCcw
} from 'lucide-react';

export const Header = () => {
  const { 
    searchQuery, 
    setSearchQuery, 
    activeTab, 
    setActiveTab, 
    setIsNewModalOpen, 
    currentAgent, 
    setCurrentAgent,
    darkMode, 
    toggleDarkMode,
    exportToCsv,
    resetToSampleData,
    filteredComplaints,
    complaints
  } = useWorkbench();

  return (
    <header className="sticky top-0 z-30 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3 min-w-max">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-700 via-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">APEX BANK</span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                  Workbench 4.0
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Internal Dispute & Regulatory Resolution</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="hidden md:flex items-center bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl border border-slate-200 dark:border-slate-700/60">
            <button
              onClick={() => setActiveTab('queue')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'queue'
                  ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <ListFilter className="h-4 w-4" />
              <span>Dispute Queue</span>
              <span className="px-1.5 py-0.2 rounded-md bg-slate-200/80 dark:bg-slate-800 text-[11px] font-mono">
                {complaints.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'analytics'
                  ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              <span>Analytics & SLAs</span>
            </button>

            <button
              onClick={() => setActiveTab('compliance')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'compliance'
                  ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              <span>CFPB & Regulatory</span>
            </button>
          </div>

          {/* Quick Search */}
          <div className="flex-1 max-w-md hidden lg:block">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 dark:text-slate-500" />
              <input
                type="text"
                placeholder="Search by customer, case #, account, or narrative..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-8 py-2 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/60 rounded-xl text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all font-medium"
              />
              {searchQuery && (
                <button 
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          {/* User Persona & Actions */}
          <div className="flex items-center gap-2.5">
            {/* Agent Switcher */}
            <div className="hidden sm:flex items-center gap-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 rounded-xl px-2.5 py-1.5">
              <div className="h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 flex items-center justify-center font-bold text-xs">
                {currentAgent.split(' ').map(n => n[0]).join('')}
              </div>
              <select
                value={currentAgent}
                onChange={(e) => setCurrentAgent(e.target.value)}
                className="bg-transparent text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none cursor-pointer"
              >
                {mockAgents.map(a => (
                  <option key={a.id} value={a.name} className="dark:bg-slate-900 text-slate-800 dark:text-slate-200">
                    {a.name} ({a.role.split(' ')[0]})
                  </option>
                ))}
              </select>
            </div>

            {/* Reset sample data */}
            <button
              onClick={resetToSampleData}
              title="Reset to sample complaints"
              className="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
            </button>

            {/* Export */}
            <button
              onClick={exportToCsv}
              title="Export complaints CSV"
              className="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition-colors"
            >
              <Download className="h-4 w-4" />
            </button>

            {/* Dark Mode */}
            <button
              onClick={toggleDarkMode}
              title="Toggle theme"
              className="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition-colors"
            >
              {darkMode ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4" />}
            </button>

            {/* Intake New Complaint */}
            <button
              onClick={() => setIsNewModalOpen(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white text-xs font-semibold rounded-xl shadow-sm shadow-blue-500/30 transition-all"
            >
              <PlusCircle className="h-4 w-4" />
              <span>Intake Case</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
