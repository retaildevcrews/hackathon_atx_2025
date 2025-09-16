import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { DecisionKitDetailPage } from '../pages/decision-kits/DecisionKitDetailPage';
import * as kitsApi from '../api/decisionKits';

jest.mock('../api/decisionKits');

const mockFetchDecisionKit = kitsApi.fetchDecisionKit as jest.Mock;
const mockAssign = kitsApi.assignRubricToDecisionKit as jest.Mock;

describe('DecisionKitDetailPage attach rubric flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('attaches a rubric inline on the detail page when no rubric is present', async () => {
    // Initial kit without rubric
    mockFetchDecisionKit.mockResolvedValueOnce({
      id: 'kit-1',
      name: 'Kit Without Rubric',
      description: 'Desc',
      candidates: [],
    });

    // assign API returns updated kit with rubricId and rubric summary
    mockAssign.mockResolvedValueOnce({
      id: 'kit-1',
      name: 'Kit Without Rubric',
      description: 'Desc',
      rubric: {
        id: 'rubric-xyz',
        name: 'R1',
        description: 'R desc',
        version: 1,
        published: true,
        criteria: []
      },
      candidates: [],
    });

    // After retry() is called, fetchDecisionKit will be called again; return updated kit
    mockFetchDecisionKit.mockResolvedValueOnce({
      id: 'kit-1',
      name: 'Kit Without Rubric',
      description: 'Desc',
      rubric: {
        id: 'rubric-xyz',
        name: 'R1',
        description: 'R desc',
        version: 1,
        published: true,
        criteria: []
      },
      candidates: [],
    });

    render(
      <MemoryRouter initialEntries={["/decision-kits/kit-1"]}>
        <Routes>
          <Route path="decision-kits/:kitId" element={<DecisionKitDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for initial load to finish and show attach UI
    await waitFor(() => expect(screen.getByText(/No rubric data available/i)).toBeInTheDocument());

  // Inline form should be visible; fill and submit
  const idInput = await screen.findByLabelText(/Rubric ID/i);
  fireEvent.change(idInput, { target: { value: 'rubric-xyz' } });
  fireEvent.click(screen.getByRole('button', { name: /Attach/i }));

    await waitFor(() => expect(mockAssign).toHaveBeenCalledWith('kit-1', 'rubric-xyz'));

    // After attach, the rubric details should be visible
    await waitFor(() => expect(screen.getByText('R1')).toBeInTheDocument());
    expect(screen.getByText(/Criteria: 0/)).toBeInTheDocument();
  });
});
