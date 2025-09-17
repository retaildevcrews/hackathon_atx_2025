import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { DecisionKitAttachRubricPage } from '../pages/decision-kits/DecisionKitAttachRubricPage';
import { DecisionKitDetailPage } from '../pages/decision-kits/DecisionKitDetailPage';
import * as kitsApi from '../api/decisionKits';

jest.mock('../api/decisionKits');

const mockAssign = kitsApi.assignRubricToDecisionKit as jest.Mock;
const mockFetchKit = kitsApi.fetchDecisionKit as jest.Mock;

describe('DecisionKitAttachRubricPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('attaches a rubric and navigates back to detail', async () => {
    mockAssign.mockResolvedValueOnce({ id: 'k-1' });
    // When navigated back to detail, the page will fetch the kit; provide data
    mockFetchKit.mockResolvedValueOnce({
      id: 'k-1',
      name: 'Kit One',
      description: 'D',
      rubric: { id: 'r-1', name: 'Rubric One', version: 1, published: true, criteria: [] },
      candidates: []
    });

    render(
      <MemoryRouter initialEntries={["/decision-kits/k-1/attach-rubric"]}>
        <Routes>
          <Route path="decision-kits/:kitId/attach-rubric" element={<DecisionKitAttachRubricPage />} />
          <Route path="decision-kits/:kitId" element={<DecisionKitDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Page header and form should render
    expect(screen.getByText(/Attach a Rubric to Decision Kit/i)).toBeInTheDocument();
    const input = screen.getByLabelText(/Rubric ID/i);
    fireEvent.change(input, { target: { value: 'r-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Attach/i }));

    await waitFor(() => expect(mockAssign).toHaveBeenCalledWith('k-1', 'r-1'));

    // After navigation, detail page should show rubric name
    await waitFor(() => expect(screen.getByText('Rubric One')).toBeInTheDocument());
  });
});
