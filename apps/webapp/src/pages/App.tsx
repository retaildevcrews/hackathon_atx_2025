import React from 'react';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import { CriteriaTable } from '../components/CriteriaTable';

export const App: React.FC = () => {
  return (
    <>
      <AppBar position="static" color="primary" enableColorOnDark>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Criteria Manager</Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
        <Box>
          <CriteriaTable />
        </Box>
      </Container>
    </>
  );
};
