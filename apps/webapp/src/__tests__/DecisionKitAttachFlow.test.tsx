import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { DecisionKitDetailPage } from '../pages/decision-kits/DecisionKitDetailPage';
import { DecisionKitAttachRubricPage } from '../pages/decision-kits/DecisionKitAttachRubricPage';
import * as kitsApi from '../api/decisionKits';

jest.mock('../api/decisionKits');

const mockFetchDecisionKit = kitsApi.fetchDecisionKit as jest.Mock;
const mockAssign = kitsApi.assignRubricToDecisionKit as jest.Mock;

describe('DecisionKitDetailPage attach rubric flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('navigates to attach page via FAB and attaches a rubric', async () => {
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
          <Route path="decision-kits/:kitId/attach-rubric" element={<DecisionKitAttachRubricPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for initial load to finish and show attach UI
    await waitFor(() => expect(screen.getByText(/No rubric data available/i)).toBeInTheDocument());

  // Click the bottom-right FAB to navigate to the attach page
  const attachLink = screen.getByRole('link', { name: /Attach Rubric/i });
  fireEvent.click(attachLink);
  // Now on attach page, fill and submit
  const idInput = await screen.findByLabelText(/Rubric ID/i);
  fireEvent.change(idInput, { target: { value: 'rubric-xyz' } });
  fireEvent.click(screen.getByRole('button', { name: /Attach/i }));

    await waitFor(() => expect(mockAssign).toHaveBeenCalledWith('kit-1', 'rubric-xyz'));

    // After attach and retry, the rubric details should be visible
    await waitFor(() => expect(screen.getByText('R1')).toBeInTheDocument());
    expect(screen.getByText(/Criteria: 0/)).toBeInTheDocument();
  });
});
