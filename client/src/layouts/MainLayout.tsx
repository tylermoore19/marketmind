import { ReactNode, useState } from "react";
import { Box, Container, Fade } from "@mui/material";
import { useAlert } from '../context/AlertContext';
import { Alert } from '@mui/material';
import Navbar from '../components/navigation/Navbar';
import Footer from '../components/navigation/Footer';
import SideDrawer from '../components/navigation/SideDrawer';

interface Props {
  children: ReactNode;
}

const MainLayout = ({ children }: Props) => {
  const [pageTitle, setPageTitle] = useState("");

  const { alert, hideAlert } = useAlert();

  // TODO : create Toast component that allows for multiple alerts, not just one

  // TODO : also fix toast message. it looks a little off center due to the side drawer

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'row',
      minHeight: '100vh',
      width: '100vw',
      position: 'relative'
    }}>
      <SideDrawer setPageTitle={setPageTitle} />

      <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1, position: 'relative' }}>
        {/* Toast */}
        <Box sx={{ position: 'absolute', top: 24, left: 0, right: 0, zIndex: 1400, display: 'flex', justifyContent: 'center', pointerEvents: 'none' }}>
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

        <Navbar pageTitle={pageTitle} />

        <Container
          component="main"
          maxWidth={false}
          sx={{
            flexGrow: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: { xs: 2, sm: 3, md: 4 },
            p: { xs: 2, sm: 3, md: 4 },
            height: 'calc(100vh - 64px)', // 64px navbar
            width: '100%',
            overflow: 'auto',
          }}
        >
          {children}
        </Container>
      </Box>
      {/* <Footer /> */}
    </Box>
  );
};

export default MainLayout;
