import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './pages/App';
import { CssBaseline } from '@mui/material';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <CssBaseline />
    <App />
  </React.StrictMode>
);
