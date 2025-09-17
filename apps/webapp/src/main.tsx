import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './pages/App';
import { CssBaseline } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { getAppTheme, type ThemeMode } from './theme';
import { createContext, useMemo, useState } from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import './styles.css';

export const ColorModeContext = createContext<{ mode: ThemeMode; toggleTheme: () => void }>({
  mode: 'light',
  toggleTheme: () => {},
});

const Root: React.FC = () => {
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState<ThemeMode>(() => {
    const saved = typeof window !== 'undefined' ? localStorage.getItem('theme-mode') : null;
    if (saved === 'light' || saved === 'dark') return saved;
    return prefersDark ? 'dark' : 'light';
  });

  const colorMode = useMemo(
    () => ({
      mode,
      toggleTheme: () =>
        setMode((m) => {
          const next = m === 'light' ? 'dark' : 'light';
          try {
            localStorage.setItem('theme-mode', next);
          } catch {
            // ignore write failures (private mode or storage disabled)
          }
          return next;
        }),
    }),
    [mode]
  );

  const theme = useMemo(() => getAppTheme(mode), [mode]);

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
};

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
