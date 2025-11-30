import Home from '../pages/Home';
import LoginPage from '../pages/LoginPage';
import SignUpPage from '../pages/SignUpPage';
import DashboardPage from '../pages/DashboardPage';
import StocksPage from '../pages/StocksPage';
import SportsPage from '../pages/SportsPage';

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
    path: '/dashboard',
    element: <DashboardPage />,
  },
  {
    path: '/stocks',
    element: <StocksPage />,
  },
  {
    path: '/sports',
    element: <SportsPage />,
  },
  {
    path: '/trips',
    element: <Home />, // Temporarily using Home component
  }
];