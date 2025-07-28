import { useState } from 'react';
import PropTypes from 'prop-types';
import { TextField, Button, Box, InputAdornment, IconButton, Typography, Alert } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useAlert } from '../context/AlertContext';

// TODO : also, add in Alert to app level so when you login or sign up, and it will navigate to next page, it will show success message

const LoginForm = ({ onSubmit }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState({});
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [alert, setAlert] = useState('');
    const { login } = useAuth();
    const { showAlert } = useAlert();

    const navigate = useNavigate();

    const validate = () => {
        const newErrors = {};
        if (!email) {
            newErrors.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            newErrors.email = 'Invalid email address';
        }
        if (!password) {
            newErrors.password = 'Password is required';
        } else if (password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setAlert('');
        if (validate()) {
            setLoading(true);
            try {
                const data = await api.login(email, password);

                if (data.token) {
                    login(data.token); // Save token in context
                    onSubmit && onSubmit({ email, password, token: data.token });
                    showAlert('Login successful', 'success');
                    navigate('/dashboard'); // redirect on success
                }
            } catch (err) {
                setAlert(err.message || 'Login failed. Please try again.');
            } finally {
                setLoading(false);
            }
        }
    };

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
                width: '100%',
                maxWidth: 350,
                mx: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
                boxShadow: 3,
                borderRadius: 2,
                p: 4,
                bgcolor: 'background.paper',
                '& input:-webkit-autofill': {
                    WebkitBoxShadow: '0 0 0 1000px #fff inset',
                    boxShadow: '0 0 0 1000px #fff inset',
                    WebkitTextFillColor: '#222',
                },
            }}
        >
            <Box sx={{ mb: 1 }}>
                <Box component="h2" sx={{ textAlign: 'center', fontWeight: 600, fontSize: 24, mb: 1 }}>
                    Login to Your Account
                </Box>
            </Box>
            {alert && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {alert}
                </Alert>
            )}
            <TextField
                id="email"
                label="Email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                error={!!errors.email}
                helperText={errors.email}
                fullWidth
                margin="dense"
                autoComplete="email"
                sx={{ mb: 0.5 }}
            />
            <TextField
                id="password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                error={!!errors.password}
                helperText={errors.password}
                fullWidth
                margin="dense"
                autoComplete="current-password"
                InputProps={{
                    endAdornment: (
                        <InputAdornment position="end">
                            <IconButton
                                aria-label={showPassword ? 'Hide password' : 'Show password'}
                                onClick={() => setShowPassword((show) => !show)}
                                edge="end"
                            >
                                {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                        </InputAdornment>
                    ),
                }}
            />
            <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 1 }} disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
            </Button>
            <Box sx={{ mt: 1, textAlign: 'center' }}>
                <Typography variant="body2">
                    Don&apos;t have an account?{' '}
                    <Button variant="text" size="small" onClick={() => navigate('/signup')} sx={{ textTransform: 'none', p: 0, minWidth: 0 }}>
                        Sign up
                    </Button>
                </Typography>
            </Box>
        </Box>
    );
};

LoginForm.propTypes = {
    onSubmit: PropTypes.func,
};

export default LoginForm;
