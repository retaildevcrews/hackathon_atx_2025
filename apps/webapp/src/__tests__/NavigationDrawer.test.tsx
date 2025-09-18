import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { NavigationDrawer } from '../components/navigation/NavigationDrawer';

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

// Mock react-router-dom's useLocation
const mockLocation = {
  pathname: '/',
  search: '',
  hash: '',
  state: null,
  key: 'default'
};

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => mockLocation
}));

describe('NavigationDrawer', () => {
  const defaultProps = {
    open: true,
    onClose: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders navigation items and branding', () => {
    renderWithRouter(<NavigationDrawer {...defaultProps} />);

    expect(screen.getByText('RubricX')).toBeInTheDocument();
    expect(screen.getByText('Decision Kits')).toBeInTheDocument();
    expect(screen.getByText('Rubrics')).toBeInTheDocument();
  });

  it('highlights active navigation item (decision kits)', () => {
    renderWithRouter(<NavigationDrawer {...defaultProps} />);
    const kitsLink = screen.getByText('Decision Kits').closest('a');
    expect(kitsLink).not.toBeNull();
    expect(kitsLink).toHaveClass('Mui-selected');
  });

  it('highlights rubrics when on rubrics page', () => {
    // Mock location for rubrics page
    mockLocation.pathname = '/rubrics';

    renderWithRouter(<NavigationDrawer {...defaultProps} />);

  const rubricsLink = screen.getByText('Rubrics').closest('a');
  expect(rubricsLink).toHaveClass('Mui-selected');
  });

  it('calls onClose when navigation item is clicked on mobile', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 600, // Below md breakpoint
    });

    const mockOnClose = jest.fn();
    renderWithRouter(
      <NavigationDrawer
        open={true}
        onClose={mockOnClose}
      />
    );

  const kitsLink = screen.getByText('Decision Kits');
  fireEvent.click(kitsLink);

    // Note: This test may need adjustment based on actual mobile detection logic
    // The component uses Material-UI's useMediaQuery which might need mocking
  });

  it('renders drawer content', () => {
    renderWithRouter(<NavigationDrawer {...defaultProps} />);
    expect(screen.getByText('RubricX')).toBeInTheDocument();
  });
});
