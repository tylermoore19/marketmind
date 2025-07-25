import { Box, Container } from '@mui/material';
import Navbar from '../components/navigation/Navbar';
import Footer from '../components/navigation/Footer';
import PropTypes from 'prop-types';

const MainLayout = ({ children }) => {
  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      width: '100%',
      position: 'relative'
    }}>
      <Navbar />
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
