import { Box, Container, Fade } from '@mui/material';
import { useAlert } from '../context/AlertContext';
import { Alert } from '@mui/material';
import Navbar from '../components/navigation/Navbar';
import Footer from '../components/navigation/Footer';
import PropTypes from 'prop-types';

const MainLayout = ({ children }) => {
  const { alert, hideAlert } = useAlert();

  // TODO : create Toast component that allows for multiple alerts, not just one

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      width: '100%',
      position: 'relative'
    }}>
      <Navbar />
      <Box sx={{ position: 'fixed', top: 24, left: 0, right: 0, zIndex: 1400, display: 'flex', justifyContent: 'center', pointerEvents: 'none' }}>
        <Fade in={!!alert} timeout={{ enter: 300, exit: 300 }} unmountOnExit>
          <Alert
            severity={alert?.severity}
            sx={{ width: 'fit-content', minWidth: 600, maxWidth: 720, px: 3, py: 1.5, borderRadius: 2, boxShadow: 3, pointerEvents: 'auto', alignItems: 'center' }}
            action={
              <Box sx={{ ml: 2, display: 'flex', alignItems: 'center', height: 'auto', pb: '4px' }}>
                <span
                  style={{
                    cursor: 'pointer',
                    fontWeight: 700,
                    fontSize: 20,
                    color: '#888',
                    lineHeight: 1,
                    display: 'flex',
                    alignItems: 'center',
                    height: '100%',
                  }}
                  onClick={hideAlert}
                  aria-label="Close alert"
                  role="button"
                >
                  ×
                </span>
              </Box>
            }
          >
            {alert?.message}
          </Alert>
        </Fade>
      </Box>
      <Container
        component="main"
        maxWidth="lg"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          py: 3,
          px: { xs: 2, sm: 3, md: 4 },
          mt: 8, // height of navbar (64px = 8 * 8px)
          mb: 10,
          minHeight: 'calc(100vh - 64px - 80px)', // 64px navbar, 80px footer
          maxHeight: 'calc(100vh - 64px - 80px)',
          overflow: 'hidden',
        }}
      >
        {children}
      </Container>
      <Footer />
    </Box>
  );
};

MainLayout.propTypes = {
  children: PropTypes.node,
};

export default MainLayout;
