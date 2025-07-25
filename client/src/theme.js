import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1e293b', // dark blue
      light: '#334155',
      dark: '#0f172a',
    },
    secondary: {
      main: '#64748b', // muted blue-gray
      light: '#94a3b8',
      dark: '#475569',
    },
    background: {
      default: '#fff', // white background
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
      primary: '#1e293b', // dark blue text
      secondary: '#64748b',
    },
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
});

export default theme;
