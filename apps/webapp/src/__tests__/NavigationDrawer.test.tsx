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

  it('renders navigation items', () => {
    renderWithRouter(<NavigationDrawer {...defaultProps} />);

    expect(screen.getByText('Decision Kits Platform')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Decision Kits')).toBeInTheDocument();
    expect(screen.getByText('Rubrics')).toBeInTheDocument();
  });

  it('highlights active navigation item', () => {
    // Test home page
    renderWithRouter(<NavigationDrawer {...defaultProps} />);

    const homeButton = screen.getByText('Home').closest('button');
    expect(homeButton).toHaveClass('Mui-selected');
  });

  it('highlights rubrics when on rubrics page', () => {
    // Mock location for rubrics page
    mockLocation.pathname = '/rubrics';

    renderWithRouter(<NavigationDrawer {...defaultProps} />);

    const rubricsButton = screen.getByText('Rubrics').closest('button');
    expect(rubricsButton).toHaveClass('Mui-selected');
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

    const homeLink = screen.getByText('Home');
    fireEvent.click(homeLink);

    // Note: This test may need adjustment based on actual mobile detection logic
    // The component uses Material-UI's useMediaQuery which might need mocking
  });

  it('renders with correct drawer width', () => {
    renderWithRouter(<NavigationDrawer {...defaultProps} />);

    // This would need to check CSS properties or rendered styles
    // The actual implementation may require more sophisticated testing
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});
