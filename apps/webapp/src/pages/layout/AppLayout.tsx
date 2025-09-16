import React from 'react';
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';
import { Outlet } from 'react-router-dom';

export const AppLayout: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" color="primary" enableColorOnDark>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Decision Kits</Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 6, flexGrow: 1 }}>
        <Outlet />
      </Container>
    </Box>
  );
};
