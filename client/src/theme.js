import { createTheme } from '@mui/material/styles';

const darkGray = '#0f0f0f'; // dark gray
const lightGray = '#f5f5f1'; // light gray

const theme = createTheme({
  palette: {
    primary: {
      main: darkGray,
      // light: '#334155',
      // dark: '#0f172a',
    },
    secondary: {
      main: '#64748b', // muted blue-gray // TODO : need to change this to match theme
      // light: '#94a3b8',
      // dark: '#475569',
    },
    background: {
      default: lightGray,
      paper: '#fff',
    },
    success: {
      main: '#22c55e', // green for success
    },
    error: {
      main: '#ef4444', // red for error
    },
    warning: {
      main: '#facc15', // yellow
    },
    info: {
      main: '#38bdf8', // blue
    },
    text: {
      primary: darkGray,
      secondary: lightGray,
    },
    gradients: {
      orange: 'linear-gradient(20deg, #FF5722 10%, #FF9800 50%)',
    }
  },
  components: {
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: "gray",
        },
      },
    }
  },
  typography: {
    fontFamily: '"Inter", "system-ui", "Avenir", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  appSpecific: {
    padding: { lg: 2, xl: 3 }
  }
});

export default theme;
