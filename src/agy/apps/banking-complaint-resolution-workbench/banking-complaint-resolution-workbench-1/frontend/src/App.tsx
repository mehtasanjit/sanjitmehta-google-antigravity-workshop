import React from 'react';
import { RoleProvider } from './context/RoleContext';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';

const App: React.FC = () => {
  return (
    <RoleProvider>
      <Layout>
        <Dashboard />
      </Layout>
    </RoleProvider>
  );
};

export { App };
