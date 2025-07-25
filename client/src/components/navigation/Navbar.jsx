import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
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
          Planventure
        </Typography>
        <Button color="inherit" onClick={() => navigate('/login')}>Login</Button>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;