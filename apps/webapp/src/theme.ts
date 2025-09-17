import { createTheme } from '@mui/material/styles';

// Central app theme: dark mode with green as the primary brand color
export type ThemeMode = 'light' | 'dark';

export const getAppTheme = (mode: ThemeMode) =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: '#228B22', // forest green
        light: '#4CAF50',
        dark: '#1B5E20',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#808000', // olive green
        light: '#9AA400',
        dark: '#666600',
        contrastText: '#ffffff',
      },
      ...(mode === 'light'
        ? {
            background: {
              default: '#f7f9f7',
              paper: '#ffffff',
            },
          }
        : {
            background: {
              default: '#0e130e',
              paper: '#121a12',
            },
          }),
    },
    components: {
      MuiAppBar: {
        styleOverrides: {
          colorPrimary: {
            backgroundColor: mode === 'light' ? '#1f7a1f' : '#104d10',
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            textTransform: 'none',
            fontWeight: 600,
            '&.Mui-focusVisible': {
              boxShadow: '0 0 0 3px rgba(34,139,34,0.35)',
            },
          },
          containedPrimary: {
            backgroundColor: '#228B22',
            '&:hover': {
              backgroundColor: '#1e7a1e',
            },
          },
          containedSecondary: {
            backgroundColor: '#808000',
            '&:hover': {
              backgroundColor: '#6e6e00',
            },
          },
        },
      },
      MuiLink: {
        styleOverrides: {
          root: {
            color: '#1e7a1e',
            '&:hover': { color: '#145214' },
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          indicator: {
            backgroundColor: '#228B22',
            height: 3,
            borderRadius: 2,
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            '&.Mui-selected': {
              color: '#228B22',
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontWeight: 600,
          },
          colorPrimary: {
            backgroundColor: '#E6F4EA',
            color: '#1e7a1e',
          },
          colorSecondary: {
            backgroundColor: '#F4F4E6',
            color: '#666600',
          },
        },
      },
      MuiFab: {
        styleOverrides: {
          primary: {
            backgroundColor: '#228B22',
            '&:hover': {
              backgroundColor: '#1e7a1e',
            },
          },
          secondary: {
            backgroundColor: '#808000',
            '&:hover': {
              backgroundColor: '#6e6e00',
            },
          },
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#228B22',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#228B22',
              borderWidth: 2,
            },
          },
          notchedOutline: {
            // subtle default outline to match palette
          },
        },
      },
      MuiInputLabel: {
        styleOverrides: {
          root: {
            '&.Mui-focused': {
              color: '#228B22',
            },
          },
        },
      },
      MuiFormLabel: {
        styleOverrides: {
          root: {
            '&.Mui-focused': {
              color: '#228B22',
            },
          },
        },
      },
      MuiCheckbox: {
        styleOverrides: {
          root: {
            '&.Mui-checked': {
              color: '#228B22',
            },
          },
        },
      },
      MuiRadio: {
        styleOverrides: {
          root: {
            '&.Mui-checked': {
              color: '#228B22',
            },
          },
        },
      },
      MuiSwitch: {
        styleOverrides: {
          switchBase: {
            '&.Mui-checked': {
              color: '#228B22',
            },
            '&.Mui-checked + .MuiSwitch-track': {
              backgroundColor: '#228B22',
            },
          },
          track: {
            backgroundColor: mode === 'light' ? '#cfe8d1' : '#2e3b2e',
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            '&.Mui-selected': {
              backgroundColor: 'rgba(34,139,34,0.12)',
            },
            '&.Mui-selected:hover': {
              backgroundColor: 'rgba(34,139,34,0.18)',
            },
          },
        },
      },
      MuiMenuItem: {
        styleOverrides: {
          root: {
            '&.Mui-selected': {
              backgroundColor: 'rgba(34,139,34,0.12)',
            },
            '&.Mui-selected:hover': {
              backgroundColor: 'rgba(34,139,34,0.18)',
            },
          },
        },
      },
      MuiCssBaseline: {
        styleOverrides: {
          '::selection': {
            backgroundColor: '#228B22',
            color: '#ffffff',
          },
          '::-moz-selection': {
            backgroundColor: '#228B22',
            color: '#ffffff',
          },
        },
      },
    },
  });
