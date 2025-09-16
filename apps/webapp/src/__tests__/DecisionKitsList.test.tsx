import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { App } from '../pages/App';

jest.mock('../hooks/useDecisionKits', () => ({
  useDecisionKits: () => ({
    kits: [
      { id: 'kit-alpha-id', name: 'Kit Alpha', description: 'First kit' },
      { id: 'kit-beta-id', name: 'Kit Beta', description: 'Second kit' }
    ],
    loading: false,
    error: null,
    retry: jest.fn()
  })
}));

jest.mock('../hooks/useDecisionKit', () => ({
  useDecisionKit: (id: string) => ({
    kit: id === 'kit-alpha-id' ? {
      id: 'kit-alpha-id',
      name: 'Kit Alpha',
      description: 'First kit',
      rubric: { id: 'rubric-r', name: 'Rubric R', version: 1, published: true, criteria: [{ criteria_id: 'crit-10', weight: 5, name: 'Crit' }] },
      candidates: [{ id: 'cand-100', name: 'Candidate A', description: 'A desc' }]
    } : null,
    loading: false,
    error: null,
    retry: jest.fn()
  })
}));

describe('Decision Kits List Page', () => {
  it('renders kits and navigates to detail', () => {
    render(<App />);
    expect(screen.getByText(/Kit Alpha/i)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Kit Alpha/i));
    // After navigation, detail page should show kit name as heading
    expect(screen.getByRole('heading', { name: /Kit Alpha/i })).toBeInTheDocument();
    expect(screen.getByText(/Criteria: 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Candidates \(1\)/i)).toBeInTheDocument();
  });
});
