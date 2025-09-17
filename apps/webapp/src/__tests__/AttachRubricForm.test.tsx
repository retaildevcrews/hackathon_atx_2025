import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AttachRubricForm } from '../components/AttachRubricForm';
import * as rubricsApi from '../api/rubrics';

jest.mock('../api/rubrics');

const mockFetchRubricSummary = rubricsApi.fetchRubricSummary as jest.Mock;

describe('AttachRubricForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows error when previewing without an id and disables attach', async () => {
    const onAttach = jest.fn();
    render(<AttachRubricForm onAttach={onAttach} />);
    // Attach should be disabled when there is no id
    expect(screen.getByRole('button', { name: /Attach/i })).toBeDisabled();
    // Preview should surface the validation error
    fireEvent.click(screen.getByRole('button', { name: /Preview/i }));
    expect(await screen.findByText(/Please enter a rubric id/i)).toBeInTheDocument();
    expect(onAttach).not.toHaveBeenCalled();
  });

  it('previews rubric summary when Preview is clicked', async () => {
    const onAttach = jest.fn();
    mockFetchRubricSummary.mockResolvedValueOnce({
      id: 'rubric-1',
      name: 'Sample Rubric',
      description: 'Desc',
      version: 1,
      published: true,
      criteria: [{ criteria_id: 1, weight: 1 }]
    });

    render(<AttachRubricForm onAttach={onAttach} />);
    const input = screen.getByLabelText(/Rubric ID/i);
    fireEvent.change(input, { target: { value: 'rubric-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Preview/i }));

    await waitFor(() => expect(screen.getByText('Sample Rubric')).toBeInTheDocument());
    expect(screen.getByText(/Criteria: 1/)).toBeInTheDocument();
  });

  it('calls onAttach with provided id', async () => {
    const onAttach = jest.fn().mockResolvedValue(undefined);
    render(<AttachRubricForm onAttach={onAttach} />);
    const input = screen.getByLabelText(/Rubric ID/i);
    fireEvent.change(input, { target: { value: 'rubric-123' } });
    fireEvent.click(screen.getByRole('button', { name: /Attach/i }));

    await waitFor(() => expect(onAttach).toHaveBeenCalledWith('rubric-123'));
  });
});
