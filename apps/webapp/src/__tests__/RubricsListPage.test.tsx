import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { RubricsListPage } from '../pages/rubrics/RubricsListPage';
import * as rubricsApi from '../api/rubrics';

// Mock the API
jest.mock('../api/rubrics');
const mockRubricsApi = rubricsApi as jest.Mocked<typeof rubricsApi>;

// Mock the useRubrics hook
jest.mock('../hooks/useRubrics');
import { useRubrics } from '../hooks/useRubrics';
const mockUseRubrics = useRubrics as jest.MockedFunction<typeof useRubrics>;

const mockRubrics = [
  {
    id: '1',
    name: 'Test Rubric 1',
    description: 'First test rubric',
    criteria: [
      { id: '1', name: 'Criteria 1', description: 'Test criteria', definition: 'Test definition' }
    ]
  },
  {
    id: '2',
    name: 'Test Rubric 2',
    description: 'Second test rubric',
    criteria: []
  }
];

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('RubricsListPage', () => {
  beforeEach(() => {
    mockUseRubrics.mockReturnValue({
      rubrics: mockRubrics,
      loading: false,
      error: null,
      retry: jest.fn()
    });
    mockRubricsApi.deleteRubric.mockResolvedValue();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the page title and create button', () => {
    renderWithRouter(<RubricsListPage />);

    expect(screen.getByRole('heading', { name: 'Rubrics' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /create rubric/i })).toBeInTheDocument();
  });

  it('displays rubrics when loaded', () => {
    renderWithRouter(<RubricsListPage />);

    expect(screen.getByText('Test Rubric 1')).toBeInTheDocument();
    expect(screen.getByText('First test rubric')).toBeInTheDocument();
    expect(screen.getByText('1 criteria')).toBeInTheDocument();

    expect(screen.getByText('Test Rubric 2')).toBeInTheDocument();
    expect(screen.getByText('Second test rubric')).toBeInTheDocument();
    expect(screen.getByText('0 criteria')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockUseRubrics.mockReturnValue({
      rubrics: null,
      loading: true,
      error: null,
      retry: jest.fn()
    });

    renderWithRouter(<RubricsListPage />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error state', () => {
    const mockRetry = jest.fn();
    mockUseRubrics.mockReturnValue({
      rubrics: null,
      loading: false,
      error: 'Failed to load rubrics',
      retry: mockRetry
    });

    renderWithRouter(<RubricsListPage />);
    expect(screen.getByText('Failed to load rubrics')).toBeInTheDocument();

    const retryButton = screen.getByRole('button', { name: 'Retry' });
    fireEvent.click(retryButton);
    expect(mockRetry).toHaveBeenCalled();
  });

  it('filters rubrics by search term', () => {
    renderWithRouter(<RubricsListPage />);

    const searchInput = screen.getByPlaceholderText('Search rubrics...');
    fireEvent.change(searchInput, { target: { value: 'First' } });

    expect(screen.getByText('Test Rubric 1')).toBeInTheDocument();
    expect(screen.queryByText('Test Rubric 2')).not.toBeInTheDocument();
  });

  it('opens delete confirmation dialog', () => {
    renderWithRouter(<RubricsListPage />);

    const deleteButtons = screen.getAllByLabelText('delete');
    fireEvent.click(deleteButtons[0]);

    expect(screen.getByText('Delete Rubric')).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument();
  });

  it('handles rubric deletion', async () => {
    renderWithRouter(<RubricsListPage />);

    const deleteButtons = screen.getAllByLabelText('delete');
    fireEvent.click(deleteButtons[0]);

    const confirmButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(mockRubricsApi.deleteRubric).toHaveBeenCalledWith('1');
    });
  });

  it('shows empty state when no rubrics', () => {
    mockUseRubrics.mockReturnValue({
      rubrics: [],
      loading: false,
      error: null,
      retry: jest.fn()
    });

    renderWithRouter(<RubricsListPage />);
    expect(screen.getByText('No rubrics available.')).toBeInTheDocument();
  });
});
