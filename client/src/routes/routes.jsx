import Home from '../pages/Home';
import LoginPage from '../pages/LoginPage';
import SignUpPage from '../pages/SignUpPage';

export const publicRoutes = [
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/login',
    element: <LoginPage />, // Now using LoginPage
  },
  {
    path: '/signup',
    element: <SignUpPage />, // Now using SignUpPage
  },
];

export const protectedRoutes = [
  {
    path: '/trips',
    element: <Home />, // Temporarily using Home component
  }
];