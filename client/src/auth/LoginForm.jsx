import { useState } from 'react';
import PropTypes from 'prop-types';
import { TextField, Button, Box, InputAdornment, IconButton, Typography } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const LoginForm = ({ onSubmit }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState({});
    const [showPassword, setShowPassword] = useState(false);
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

    const handleSubmit = (e) => {
        e.preventDefault();
        if (validate()) {
            onSubmit && onSubmit({ email, password });
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
                gap: 1, // reduced gap from 2 to 1
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
                    Login to Your Account
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
                margin="dense" // changed from "normal" to "dense"
                autoComplete="email"
                sx={{ mb: 0.5 }} // smaller gap below email
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
                margin="dense" // changed from "normal" to "dense"
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
            <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 1 }}>
                Login
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
