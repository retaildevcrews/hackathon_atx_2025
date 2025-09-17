import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { RubricForm } from '../components/RubricForm';

jest.mock('../hooks/useCriteria', () => ({
  useCriteria: () => ({
    criteria: [
      { id: '1', name: 'Accuracy', description: 'Accuracy desc', definition: 'Acc def' },
      { id: '2', name: 'Completeness', description: 'Comp desc', definition: 'Comp def' },
      { id: '3', name: 'Clarity', description: 'Clarity desc', definition: 'Cla def' },
    ],
    refresh: jest.fn(),
  }),
}));

describe('RubricForm edit mode', () => {
  it('renders initial values and saves updates', () => {
    const initialRubric = {
      id: 'r1',
      name: 'Initial Name',
      description: 'Initial description',
      criteria: [
        { id: '2', name: 'Completeness', description: 'Comp desc', definition: 'Comp def' },
      ],
    };
    const onSave = jest.fn();

    render(<RubricForm initialRubric={initialRubric} onSave={onSave} />);

    expect(screen.getByLabelText(/Name/i)).toHaveValue('Initial Name');
    expect(screen.getByLabelText(/Description/i)).toHaveValue('Initial description');
    // Existing selected criterion should be checked
    const completeness = screen.getByLabelText(/Completeness/i) as HTMLInputElement;
    expect(completeness.checked).toBe(true);

    // Change name and toggle another criterion
    fireEvent.change(screen.getByLabelText(/Name/i), { target: { value: 'Updated Name' } });
    fireEvent.click(screen.getByLabelText(/Accuracy/i));

    // Submit
    fireEvent.click(screen.getByText('Save Rubric'));

    // Assert payload without depending on array order
    expect(onSave).toHaveBeenCalledTimes(1);
    const payload = (onSave as jest.Mock).mock.calls[0][0];
    expect(payload.name).toBe('Updated Name');
    expect(payload.description).toBe('Initial description');
    expect(payload.criteria).toHaveLength(2);
    expect(payload.criteria).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ id: '1', name: 'Accuracy' }),
        expect.objectContaining({ id: '2', name: 'Completeness' }),
      ])
    );
  });
});
