import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { RubricForm } from '../components/RubricForm';
import { Criteria } from '../types/rubric';

const mockCriteria: Criteria[] = [
  { id: '1', name: 'Criterion 1', description: 'Desc 1', definition: 'Def 1' },
  { id: '2', name: 'Criterion 2', description: 'Desc 2', definition: 'Def 2' }
];

jest.mock('../hooks/useCriteria', () => ({
  useCriteria: () => ({ criteria: mockCriteria, refresh: jest.fn() })
}));

describe('RubricForm', () => {
  it('validates required fields', () => {
    const onSave = jest.fn();
    render(<RubricForm onSave={onSave} />);
    fireEvent.click(screen.getByText(/Save Rubric/i));
    expect(screen.getByText(/Name is required/i)).toBeInTheDocument();
  });

  it('validates criteria selection', () => {
    const onSave = jest.fn();
    render(<RubricForm onSave={onSave} />);
    fireEvent.change(screen.getByLabelText(/Name:/i), { target: { value: 'Test Rubric' } });
    fireEvent.change(screen.getByLabelText(/Description:/i), { target: { value: 'Test Description' } });
    fireEvent.click(screen.getByText(/Save Rubric/i));
    expect(screen.getByText(/select at least one criterion/i)).toBeInTheDocument();
  });

  it('calls onSave with valid data', () => {
    const onSave = jest.fn();
    render(<RubricForm onSave={onSave} />);
    fireEvent.change(screen.getByLabelText(/Name:/i), { target: { value: 'Test Rubric' } });
    fireEvent.change(screen.getByLabelText(/Description:/i), { target: { value: 'Test Description' } });
    fireEvent.click(screen.getByLabelText(/Criterion 1/i));
    fireEvent.click(screen.getByText(/Save Rubric/i));
    expect(onSave).toHaveBeenCalledWith({
      name: 'Test Rubric',
      description: 'Test Description',
      criteria: [mockCriteria[0]]
    });
  });
});
