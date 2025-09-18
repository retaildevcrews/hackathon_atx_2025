import React, { useContext, useRef, useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  IconButton
} from '@mui/material';
import { Menu as MenuIcon, DarkMode, LightMode } from '@mui/icons-material';
import { Outlet, Link } from 'react-router-dom';
import { NavigationDrawer } from '../../components/navigation/NavigationDrawer';
import { ColorModeContext } from '../../main';

export const AppLayout: React.FC = () => {
  // Drawer should be open by default on desktop but closed on mobile; keep simple default true
  const [drawerOpen, setDrawerOpen] = useState(true);
  const { mode, toggleTheme } = useContext(ColorModeContext);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
  };

  // Focus management: focus main content after drawer closes for a11y
  const mainRef = useRef<HTMLDivElement | null>(null);
  const handleDrawerClosedFocusMain = () => {
    // Slight delay to allow drawer unmount/transition
    requestAnimationFrame(() => {
      mainRef.current?.focus();
    });
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        color="primary"
        sx={{
          width: '100%',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          transition: (theme) => theme.transitions.create(['margin-left'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label={drawerOpen ? 'collapse menu' : 'expand menu'}
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h6"
            noWrap
            component={Link}
            to="/"
            sx={{
              textDecoration: 'none',
              color: 'inherit',
              '&:hover': { opacity: 0.85 },
              cursor: 'pointer'
            }}
          >
            RubricX
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <IconButton color="inherit" aria-label="toggle theme" onClick={toggleTheme}>
            {mode === 'dark' ? <LightMode /> : <DarkMode />}
          </IconButton>
        </Toolbar>
      </AppBar>

      <NavigationDrawer
        open={drawerOpen}
        onClose={handleDrawerClose}
        onClosed={handleDrawerClosedFocusMain}
      />

      <Box
        component="main"
        ref={mainRef}
        tabIndex={-1}
        aria-label="Main content"
        sx={{
          flexGrow: 1,
          // Content no longer shifts when drawer opens; overlay behavior retains left alignment
        }}
      >
        <Toolbar /> {/* This toolbar acts as spacer for fixed AppBar */}
        <Container maxWidth="lg" sx={{ mt: 4, mb: 6, px: { xs: 2, sm: 3 } }}>
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
};
