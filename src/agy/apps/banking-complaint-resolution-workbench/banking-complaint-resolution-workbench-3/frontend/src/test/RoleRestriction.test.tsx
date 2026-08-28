import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('Role-Based Registration Restrictions', () => {
  it('allows Intake Specialist to see and click Register Complaint', () => {
    render(<App />);
    
    // Default role is Intake Specialist, so Register Complaint button should be visible
    const registerBtn = screen.queryByRole('button', { name: /Register Complaint/i });
    expect(registerBtn).toBeInTheDocument();
  });

  it('hides Register Complaint button for Investigator role', () => {
    render(<App />);
    
    // Switch active role to Investigator
    const roleSelector = screen.getByLabelText(/Active Role:/i);
    fireEvent.change(roleSelector, { target: { value: 'Investigator' } });
    
    // Register Complaint button should not be rendered
    const registerBtn = screen.queryByRole('button', { name: /Register Complaint/i });
    expect(registerBtn).not.toBeInTheDocument();
  });

  it('redirects Investigator from new-complaint view to dashboard', () => {
    render(<App />);
    
    // First navigate to Register Complaint as Intake Specialist
    const registerBtn = screen.getByRole('button', { name: /Register Complaint/i });
    fireEvent.click(registerBtn);
    expect(screen.getByRole('heading', { name: /Complaint Intake Form/i })).toBeInTheDocument();
    
    // Now switch active role to Investigator
    const roleSelector = screen.getByLabelText(/Active Role:/i);
    fireEvent.change(roleSelector, { target: { value: 'Investigator' } });
    
    // Should be automatically redirected back to Overview Dashboard
    expect(screen.queryByRole('heading', { name: /Complaint Intake Form/i })).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Overview Dashboard/i })).toBeInTheDocument();
  });
});
