import { useState } from 'react';
import PropTypes from 'prop-types';
import { TextField, Button, Box, InputAdornment, IconButton, Typography } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const SignUpForm = ({ onSubmit }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errors, setErrors] = useState({});
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
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
        if (!confirmPassword) {
            newErrors.confirmPassword = 'Please confirm your password';
        } else if (password !== confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (validate()) {
            onSubmit && onSubmit({ email, password });
        }
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'background.default',
            }}
        >
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
                    // Prevent Chrome autofill from graying out fields
                    '& input:-webkit-autofill': {
                        WebkitBoxShadow: '0 0 0 1000px #fff inset',
                        boxShadow: '0 0 0 1000px #fff inset',
                        WebkitTextFillColor: '#222', // set to dark text for visibility
                    },
                }}
            >
                <Box sx={{ mb: 1 }}>
                    <Box component="h2" sx={{ textAlign: 'center', fontWeight: 600, fontSize: 24, mb: 1 }}>
                        Create an Account
                    </Box>
                </Box>
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
                    autoComplete="new-password"
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
                <TextField
                    id="confirmPassword"
                    label="Confirm Password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    error={!!errors.confirmPassword}
                    helperText={errors.confirmPassword}
                    fullWidth
                    margin="dense"
                    autoComplete="new-password"
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton
                                    aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                                    onClick={() => setShowConfirmPassword((show) => !show)}
                                    edge="end"
                                >
                                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </InputAdornment>
                        ),
                    }}
                />
                <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 1 }}>
                    Sign Up
                </Button>
                <Box sx={{ mt: 1, textAlign: 'center' }}>
                    <Typography variant="body2">
                        Already have an account?{' '}
                        <Button variant="text" size="small" onClick={() => navigate('/login')} sx={{ textTransform: 'none', p: 0, minWidth: 0 }}>
                            Log in
                        </Button>
                    </Typography>
                </Box>
            </Box>
        </Box>
    );
};

SignUpForm.propTypes = {
    onSubmit: PropTypes.func,
};

export default SignUpForm;
