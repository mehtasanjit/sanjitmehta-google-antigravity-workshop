import { render, screen, fireEvent, within } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('Banking Complaint Kanban Board & Transitions', () => {
  it('renders the four Kanban status columns', () => {
    render(<App />);
    
    // Check for the 4 standard Kanban column headers
    expect(screen.getByText(/New complaints/i)).toBeInTheDocument();
    expect(screen.getByText(/Assigned/i)).toBeInTheDocument();
    expect(screen.getByText(/In Progress/i)).toBeInTheDocument();
    expect(screen.getByText(/Resolved/i)).toBeInTheDocument();
  });

  it('displays the correct context-aware action buttons on cards based on status and active role', () => {
    render(<App />);
    
    // Check that we have the Kanban column containers
    const newColumn = screen.getByTestId('column-New');
    expect(newColumn).toBeInTheDocument();
    
    // Under default role "Intake Specialist", New cards should show "Assign to Specialist"
    const assignBtn = within(newColumn).getAllByRole('button', { name: /Assign/i })[0];
    expect(assignBtn).toBeInTheDocument();
    expect(assignBtn).not.toBeDisabled();
    
    // Switch role to "Investigator"
    const roleSelector = screen.getByLabelText(/Active Role:/i);
    fireEvent.change(roleSelector, { target: { value: 'Investigator' } });
    
    // For Investigator, "Assign" button on New card should be disabled or hidden
    expect(assignBtn).toBeDisabled();
  });

  it('opens a details drawer when a complaint card is clicked', () => {
    render(<App />);
    
    // Click on a complaint card (e.g. John Doe's complaint)
    const card = screen.getByText(/John Doe/i);
    fireEvent.click(card);
    
    // Drawer should open and display full details and activity timeline
    expect(screen.getByText(/Complaint Details/i)).toBeInTheDocument();
    expect(screen.getByText(/Activity Log Timeline/i)).toBeInTheDocument();
  });
});
