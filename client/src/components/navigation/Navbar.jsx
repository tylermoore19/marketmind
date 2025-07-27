import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  const navButtonSx = (withBorder = false) => ({
    color: 'inherit',
    border: withBorder ? '1.5px solid #fff' : 'none',
    ml: withBorder ? 1 : 0,
    '&:focus': { border: withBorder ? '1.5px solid #fff' : 'none', outline: 'none' },
    '&:focus-visible': { border: withBorder ? '1.5px solid #fff' : 'none', outline: 'none' },
  });
  return (
    <AppBar
      position="static"
      sx={{
        width: '100%',
        left: 0,
        right: 0,
        position: 'fixed',
      }}
    >
      <Toolbar sx={{ width: '100%' }}>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, textAlign: 'left' }}>
          MarketMind
        </Typography>
        {isAuthenticated ? (
          <Button onClick={logout} sx={navButtonSx(true)}>
            Sign Out
          </Button>
        ) : (
          <>
            <Button onClick={() => navigate('/login')} sx={navButtonSx(false)}>Login</Button>
            <Button onClick={() => navigate('/signup')} sx={navButtonSx(true)}>Sign Up</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;