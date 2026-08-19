import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

describe('Banking Complaint Registration Form', () => {
  it('navigates to the registration form view and renders all input fields', () => {
    render(<App />);
    
    // Click "Register Complaint" menu item in sidebar
    const registerMenuBtn = screen.getByRole('button', { name: /Register Complaint/i });
    fireEvent.click(registerMenuBtn);
    
    // Check that we transitioned to the intake form view
    expect(screen.getByRole('heading', { name: /Complaint Intake Form/i })).toBeInTheDocument();
    
    // Verify all input fields are present
    expect(screen.getByLabelText(/Customer Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Account Number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Account Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Severity Level/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Detailed Description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Submit Complaint/i })).toBeInTheDocument();
  });

  it('validates required fields on submission', () => {
    render(<App />);
    
    // Navigate to registration form
    fireEvent.click(screen.getByRole('button', { name: /Register Complaint/i }));
    
    // Click submit on an empty form
    const submitBtn = screen.getByRole('button', { name: /Submit Complaint/i });
    fireEvent.click(submitBtn);
    
    // Verify that validation error messages appear
    expect(screen.getByText(/Customer name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/Detailed description is required/i)).toBeInTheDocument();
  });

  it('successfully submits a valid complaint and navigates back to dashboard', async () => {
    render(<App />);
    
    // Navigate to registration form
    fireEvent.click(screen.getByRole('button', { name: /Register Complaint/i }));
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/Customer Name/i), { target: { value: 'Sanjit Mehta' } });
    fireEvent.change(screen.getByLabelText(/Account Number/i), { target: { value: 'XXXXXX54321' } });
    fireEvent.change(screen.getByLabelText(/Account Type/i), { target: { value: 'Credit Card' } });
    fireEvent.change(screen.getByLabelText(/Severity Level/i), { target: { value: 'High' } });
    fireEvent.change(screen.getByLabelText(/Detailed Description/i), { target: { value: 'Double billing for my monthly premium. I was charged $150 twice.' } });
    
    // Submit the form
    const submitBtn = screen.getByRole('button', { name: /Submit Complaint/i });
    fireEvent.click(submitBtn);
    
    // Wait for the form to submit, transition back, and render the newly registered complaint on the dashboard
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Overview Dashboard/i })).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Sanjit Mehta/i)).toBeInTheDocument();
  });
});
