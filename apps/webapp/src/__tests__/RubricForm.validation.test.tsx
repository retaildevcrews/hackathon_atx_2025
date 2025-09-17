import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { RubricForm } from '../components/RubricForm';

// Mock useCriteria hook to provide a couple of criteria entries
jest.mock('../hooks/useCriteria', () => ({
  useCriteria: () => ({
    criteria: [
      { id: '1', name: 'Accuracy', description: 'Accuracy desc', definition: 'Acc def' },
      { id: '2', name: 'Completeness', description: 'Comp desc', definition: 'Comp def' },
    ],
    refresh: jest.fn(),
  }),
}));

describe('RubricForm validation', () => {
  it('disables submit until form valid and shows errors', () => {
    const onSave = jest.fn();
    render(<RubricForm onSave={onSave} />);

    const saveButton = screen.getByText('Save Rubric') as HTMLButtonElement;
    expect(saveButton).toBeDisabled();

    // Blur fields to show errors
    fireEvent.blur(screen.getByLabelText(/Name/i));
    fireEvent.blur(screen.getByLabelText(/Description/i));

    // Select one criterion to satisfy criteria validation
    fireEvent.click(screen.getByLabelText(/Accuracy/i));

    // Fill required fields
    fireEvent.change(screen.getByLabelText(/Name/i), { target: { value: 'My Rubric' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Some description' } });

    // Now button should be enabled
    expect(saveButton.disabled).toBe(false);

    // Submit
    fireEvent.click(saveButton);
    expect(onSave).toHaveBeenCalledWith({
      name: 'My Rubric',
      description: 'Some description',
      criteria: [
        { id: '1', name: 'Accuracy', description: 'Accuracy desc', definition: 'Acc def' },
      ],
    });
  });
});
