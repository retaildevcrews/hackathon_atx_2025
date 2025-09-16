import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import * as api from '../api/decisionKits';
import { DecisionKitListPage } from '../pages/decision-kits/DecisionKitListPage';
import { DecisionKitDetailPage } from '../pages/decision-kits/DecisionKitDetailPage';

jest.mock('../api/decisionKits');

const mockFetchDecisionKits = api.fetchDecisionKits as jest.Mock;
const mockFetchDecisionKit = api.fetchDecisionKit as jest.Mock;

describe('Decision Kits UI', () => {
  beforeEach(() => {
    mockFetchDecisionKits.mockReset();
    mockFetchDecisionKit.mockReset();
  });

  test('List page renders empty state', async () => {
    mockFetchDecisionKits.mockResolvedValueOnce([]);
    render(<MemoryRouter><DecisionKitListPage /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText(/No decision kits yet/i)).toBeInTheDocument());
  });

  test('Detail page shows rubric criteria count', async () => {
    mockFetchDecisionKit.mockResolvedValueOnce({
      id: 1,
      name: 'Kit A',
      description: 'Desc',
      rubric: { id: 10, name: 'R', version: 1, published: true, criteria: [ { criteria_id: 5, weight: 3, name: 'Crit' } ] },
      candidates: []
    });
    render(
      <MemoryRouter initialEntries={['/decision-kits/1']}>
        <Routes>
          <Route path="decision-kits/:kitId" element={<DecisionKitDetailPage />} />
        </Routes>
      </MemoryRouter>
    );
    await waitFor(() => expect(screen.getByText(/Criteria: 1/)).toBeInTheDocument());
  });
});
