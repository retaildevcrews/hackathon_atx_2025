import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DecisionKitForm } from '../components/decisionKits/DecisionKitForm';

// NOTE: This is a lightweight test focusing on form validation logic;
// full integration tests would mock axios but are deferred for brevity.

const mockRubrics = [ { id: 'r1', name: 'Rubric One' } ];

describe('DecisionKitForm', () => {
  it('validates required name', async () => {
    const handleSubmit = jest.fn();
    render(<DecisionKitForm onSubmit={handleSubmit} rubrics={mockRubrics} />);
    fireEvent.click(screen.getByRole('button', { name: /create/i }));
    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits valid data', async () => {
    const handleSubmit = jest.fn(() => Promise.resolve());
    render(<DecisionKitForm onSubmit={handleSubmit} rubrics={mockRubrics} />);
    fireEvent.change(screen.getByLabelText(/name/i), { target: { value: 'My Kit' } });
    // Select rubric
    fireEvent.mouseDown(screen.getByLabelText(/rubric/i));
    const option = await screen.findByText(/Rubric One/);
    fireEvent.click(option);
    fireEvent.click(screen.getByRole('button', { name: /create/i }));
    await waitFor(() => expect(handleSubmit).toHaveBeenCalled());
  });
});
