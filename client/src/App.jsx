import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import ProtectedRoute from './components/routing/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { AlertProvider } from './context/AlertContext';
import { publicRoutes, protectedRoutes } from './routes/routes';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <AlertProvider>
        <Router>
          <MainLayout>
            <Routes>
              {publicRoutes.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={route.element}
                />
              ))}

              {protectedRoutes.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={
                    <ProtectedRoute>
                      {route.element}
                    </ProtectedRoute>
                  }
                />
              ))}
            </Routes>
          </MainLayout>
        </Router>
      </AlertProvider>
    </AuthProvider>
  );
}

export default App;