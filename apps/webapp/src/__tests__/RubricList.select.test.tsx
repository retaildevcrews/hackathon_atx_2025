import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { RubricList } from '../components/RubricList';
import { Rubric } from '../types/rubric';

describe('RubricList', () => {
  it('calls onSelect with clicked rubric', () => {
    const rubrics: Rubric[] = [
      { id: 'r1', name: 'Rubric A', description: 'Desc A', criteria: [] },
      { id: 'r2', name: 'Rubric B', description: 'Desc B', criteria: [] },
    ];
    const onSelect = jest.fn();

    render(<RubricList rubrics={rubrics} onSelect={onSelect} />);

    fireEvent.click(screen.getByText('Rubric B'));

    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith(rubrics[1]);
  });
});
