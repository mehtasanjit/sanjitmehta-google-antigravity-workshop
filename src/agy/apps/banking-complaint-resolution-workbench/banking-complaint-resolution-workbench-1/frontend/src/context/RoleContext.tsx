import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface User {
  username: string;
  name: string;
  role: string;
}

export interface RoleContextType {
  activeUser: User;
  setActiveUser: (user: User) => void;
  users: User[];
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>;
}

const USERS: User[] = [
  { username: 'jane_doe', name: 'Jane Doe', role: 'CSR' },
  { username: 'john_smith', name: 'John Smith', role: 'Case Handler' },
  { username: 'alice_johnson', name: 'Alice Johnson', role: 'Case Handler' },
  { username: 'robert_vance', name: 'Robert Vance', role: 'Supervisor' },
];

const RoleContext = createContext<RoleContextType | undefined>(undefined);

interface RoleProviderProps {
  children: ReactNode;
}

const RoleProvider: React.FC<RoleProviderProps> = ({ children }) => {
  const [activeUser, setActiveUserInternal] = useState<User>(USERS[0]);

  const setActiveUser = (user: User) => {
    setActiveUserInternal(user);
  };

  const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
    const headers = new Headers(options.headers);
    headers.set('X-User-Name', activeUser.username);
    headers.set('X-User-Role', activeUser.role);
    headers.set('Content-Type', 'application/json');
    return fetch(url, { ...options, headers });
  };

  return (
    <RoleContext.Provider value={{ activeUser, setActiveUser, users: USERS, fetchWithAuth }}>
      {children}
    </RoleContext.Provider>
  );
};

const useRole = (): RoleContextType => {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useRole must be used within a RoleProvider');
  }
  return context;
};

export { RoleProvider, useRole, USERS };
