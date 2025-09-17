import { createTheme } from '@mui/material/styles';

// Central app theme: dark mode with green as the primary brand color
export const appTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      // Forest green primary (approx #228B22)
      main: '#228B22',
      light: '#4CAF50', // lighter variant for hovers
      dark: '#1B5E20',
      contrastText: '#ffffff',
    },
    secondary: {
      // Olive green secondary (approx #808000)
      main: '#808000',
      light: '#9AA400',
      dark: '#666600',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f7f9f7',
      paper: '#ffffff',
    },
  },
});
