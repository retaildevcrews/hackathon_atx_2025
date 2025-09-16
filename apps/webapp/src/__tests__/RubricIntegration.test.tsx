import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { App } from '../pages/App';
import { Rubric } from '../types/rubric';

const mockRubrics: Rubric[] = [
  {
    id: 'r1',
    name: 'Rubric 1',
    description: 'Desc 1',
    criteria: [
      { id: '1', name: 'Criterion 1', description: 'Desc 1', definition: 'Def 1' }
    ]
  }
];

jest.mock('../hooks/useRubric', () => ({
  useRubric: () => ({
    rubrics: mockRubrics,
    createRubric: jest.fn(),
    updateRubric: jest.fn(),
    deleteRubric: jest.fn(),
    loading: false
  })
}));

jest.mock('../hooks/useCriteria', () => ({
  useCriteria: () => ({
    criteria: [
      { id: '1', name: 'Criterion 1', description: 'Desc 1', definition: 'Def 1' },
      { id: '2', name: 'Criterion 2', description: 'Desc 2', definition: 'Def 2' }
    ],
    refresh: jest.fn()
  })
}));

describe('Rubric Integration', () => {
  it('displays rubric list and details', async () => {
    render(<App />);
    expect(screen.getByText(/Rubric 1/i)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Rubric 1/i));
    expect(screen.getByText(/Desc 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Criterion 1/i)).toBeInTheDocument();
  });

  it('shows rubric form and validates', async () => {
    render(<App />);
    fireEvent.click(screen.getByText(/Add Rubric/i));
    fireEvent.click(screen.getByText(/Save Rubric/i));
    expect(screen.getByText(/Name is required/i)).toBeInTheDocument();
  });

  it('allows editing a rubric', async () => {
    render(<App />);
    fireEvent.click(screen.getByText(/Rubric 1/i));
    fireEvent.click(screen.getByText(/Edit/i));
    expect(screen.getByDisplayValue(/Rubric 1/i)).toBeInTheDocument();
  });
});
