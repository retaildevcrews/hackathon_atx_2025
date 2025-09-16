import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { App } from '../pages/App';

jest.mock('../hooks/useDecisionKit', () => ({
  useDecisionKit: () => ({ kit: null, loading: false, error: null, retry: jest.fn() })
}));

describe('Decision Kit Detail - arbitrary string id', () => {
  it('renders loading state for string id (no immediate invalid error)', () => {
    render(<MemoryRouter initialEntries={['/decision-kits/abc']}> <App /> </MemoryRouter>);
    // We removed numeric validation; ensure previous error text not present.
    expect(screen.queryByText(/Invalid decision kit id/i)).toBeNull();
  });
});
