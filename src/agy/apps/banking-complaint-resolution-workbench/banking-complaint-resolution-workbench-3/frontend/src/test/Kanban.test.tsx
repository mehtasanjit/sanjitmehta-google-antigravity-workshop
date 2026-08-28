import { render, screen, fireEvent, within } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('Banking Complaint Kanban Board & Transitions', () => {
  it('renders the four Kanban status columns', async () => {
    render(<App />);
    
    // Wait for the async data to load by finding John Doe's card
    const customerCard = await screen.findByText(/John Doe/i);
    expect(customerCard).toBeInTheDocument();
    
    // Check for the 4 standard Kanban column headers explicitly using heading role and exact match rules
    expect(screen.getByRole('heading', { name: /New Queue/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /^Assigned$/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /In Progress/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Resolved/i })).toBeInTheDocument();
  });

  it('displays the correct context-aware action buttons on cards based on status and active role', async () => {
    render(<App />);
    
    // Wait for async data to load
    await screen.findByText(/John Doe/i);
    
    // Check that we have the Kanban column containers
    const newColumn = screen.getByTestId('column-New');
    expect(newColumn).toBeInTheDocument();
    
    // Under default role "Intake Specialist", New cards should show "Assign" button
    const assignBtn = within(newColumn).getAllByRole('button', { name: /Assign/i })[0];
    expect(assignBtn).toBeInTheDocument();
    expect(assignBtn).not.toBeDisabled();
    
    // Switch role to "Investigator"
    const roleSelector = screen.getByLabelText(/Active Role:/i);
    fireEvent.change(roleSelector, { target: { value: 'Investigator' } });
    
    // For Investigator, "Assign" button on New card should be disabled or hidden
    expect(assignBtn).toBeDisabled();
  });

  it('opens a details drawer when a complaint card is clicked', async () => {
    render(<App />);
    
    // Wait for async data to load
    const card = await screen.findByText(/John Doe/i);
    
    // Click on a complaint card
    fireEvent.click(card);
    
    // Drawer should open and display full details and activity timeline
    expect(await screen.findByText(/Complaint Details/i)).toBeInTheDocument();
    expect(screen.getByText(/Activity Log Timeline/i)).toBeInTheDocument();
  });
});
