import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('Banking Internal Complaint Tracker Dashboard', () => {
  it('renders the main layout with header and app title', () => {
    render(<App />);
    
    // Check for the main application title in the header
    const titleElement = screen.getByText(/Banking Internal Complaint Tracker/i);
    expect(titleElement).toBeInTheDocument();
  });

  it('renders the role selector dropdown in the header', () => {
    render(<App />);
    
    // Check that the role switcher select element exists
    const roleSelector = screen.getByLabelText(/Active Role:/i);
    expect(roleSelector).toBeInTheDocument();
    
    // Check that the standard roles are available
    expect(screen.getByRole('option', { name: /Intake Specialist/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /Investigator/i })).toBeInTheDocument();
  });

  it('renders the dashboard metric cards with correct labels', () => {
    render(<App />);
    
    // Check that all metric cards are rendered
    expect(screen.getByText(/Total Complaints/i)).toBeInTheDocument();
    expect(screen.getByText(/New Complaints/i)).toBeInTheDocument();
    expect(screen.getByText(/Under Investigation/i)).toBeInTheDocument();
    expect(screen.getByText(/Resolved Cases/i)).toBeInTheDocument();
  });
});
