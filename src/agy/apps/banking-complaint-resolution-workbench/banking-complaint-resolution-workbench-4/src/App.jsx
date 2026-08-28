import React from 'react';
import { WorkbenchProvider, useWorkbench } from './context/WorkbenchContext';
import { Header } from './components/Header';
import { StatsOverview } from './components/StatsOverview';
import { ComplaintQueue } from './components/ComplaintQueue';
import { ComplaintDetailView } from './components/ComplaintDetailView';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { RegulatoryComplianceView } from './components/RegulatoryComplianceView';
import { NewComplaintModal } from './components/NewComplaintModal';
import { NotificationToast } from './components/NotificationToast';

const MainLayout = () => {
  const { activeTab } = useWorkbench();

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
      <Header />

      <main className="flex-1 max-w-[1720px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* KPI Metrics Strip */}
        <StatsOverview />

        {/* Dynamic Tab Views */}
        {activeTab === 'queue' && (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
            {/* Left Queue Panel: 5 columns */}
            <div className="xl:col-span-5 w-full">
              <ComplaintQueue />
            </div>

            {/* Right Resolution Workbench: 7 columns */}
            <div className="xl:col-span-7 w-full">
              <ComplaintDetailView />
            </div>
          </div>
        )}

        {activeTab === 'analytics' && <AnalyticsDashboard />}

        {activeTab === 'compliance' && <RegulatoryComplianceView />}
      </main>

      {/* Modals & Toasts */}
      <NewComplaintModal />
      <NotificationToast />
    </div>
  );
};

export default function App() {
  return (
    <WorkbenchProvider>
      <MainLayout />
    </WorkbenchProvider>
  );
}
