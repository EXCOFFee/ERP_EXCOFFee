// ========================================================
// SISTEMA ERP UNIVERSAL - Layout Principal
// ========================================================

import { Outlet } from 'react-router-dom';
import { Box, useMediaQuery, useTheme } from '@mui/material';

import Header from '@components/layout/Header';
import Sidebar from '@components/layout/Sidebar';
import { useAppSelector, useAppDispatch } from '@hooks/redux';
import { setSidebarOpen, setSidebarCollapsed } from '@store/slices/uiSlice';

const SIDEBAR_WIDTH = 280;
const SIDEBAR_COLLAPSED_WIDTH = 64;
const HEADER_HEIGHT = 64;

function MainLayout() {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { sidebarOpen, sidebarCollapsed } = useAppSelector((state) => state.ui);
  
  const handleSidebarToggle = () => {
    if (isMobile) {
      dispatch(setSidebarOpen(!sidebarOpen));
    } else {
      dispatch(setSidebarCollapsed(!sidebarCollapsed));
    }
  };
  
  const handleSidebarClose = () => {
    dispatch(setSidebarOpen(false));
  };
  
  const sidebarWidth = sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Header */}
      <Header
        onMenuClick={handleSidebarToggle}
        sidebarWidth={isMobile ? 0 : sidebarWidth}
      />
      
      {/* Sidebar */}
      <Sidebar
        open={isMobile ? sidebarOpen : true}
        onClose={handleSidebarClose}
        collapsed={!isMobile && sidebarCollapsed}
        width={SIDEBAR_WIDTH}
        collapsedWidth={SIDEBAR_COLLAPSED_WIDTH}
        variant={isMobile ? 'temporary' : 'permanent'}
      />
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: `${HEADER_HEIGHT}px`,
          px: { xs: 2, sm: 3 },
          pb: 3,
          minHeight: '100vh',
          backgroundColor: 'background.default',
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ml: isMobile ? 0 : `${sidebarWidth}px`,
        }}
      >
        <Box sx={{ py: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}

export default MainLayout;
