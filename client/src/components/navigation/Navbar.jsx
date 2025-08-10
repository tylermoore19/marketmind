import { useState } from "react";
import PropTypes from 'prop-types';
import { AppBar, Toolbar, Typography, Menu, MenuItem, IconButton, Box } from '@mui/material';
import { AccountCircle } from "@mui/icons-material";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = ({ pageTitle }) => {
    const [anchorEl, setAnchorEl] = useState(null);

    const navigate = useNavigate();
    const { isAuthenticated, logout } = useAuth();

    const handleMenuOpen = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    // TODO : need to add name display when logged in
    // TODO : also, need to create new file that is meant for styling that can be used across app (not sure if I can use theme.js for that or not)

    return (
        <AppBar position='sticky' sx={{ left: 'auto', right: 'auto', width: '100%', bgcolor: 'background.paper', color: 'text.primary' }}>
            <Toolbar sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
                <Typography variant="h6" noWrap component="div">
                    {pageTitle}
                </Typography>

                <Box sx={{ flexGrow: 1 }} /> {/* Pushes icon to right */}

                <IconButton
                    size="large"
                    edge="end"
                    color="inherit"
                    onClick={handleMenuOpen}
                >
                    <AccountCircle />
                </IconButton>

                <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                    anchorOrigin={{
                        vertical: "bottom",
                        horizontal: "right",
                    }}
                    transformOrigin={{
                        vertical: "top",
                        horizontal: "right",
                    }}
                >
                    {!isAuthenticated ? (
                        <>
                            <MenuItem
                                onClick={() => {
                                    handleMenuClose();
                                    navigate("/login");
                                }}
                            >
                                Login
                            </MenuItem>
                            <MenuItem
                                onClick={() => {
                                    handleMenuClose();
                                    navigate("/signup");
                                }}
                            >
                                Sign Up
                            </MenuItem>
                        </>
                    ) : (
                        <MenuItem
                            onClick={() => {
                                handleMenuClose();
                                logout();
                            }}
                        >
                            Logout
                        </MenuItem>
                    )}
                </Menu>
            </Toolbar>
        </AppBar>
    );
};

Navbar.propTypes = {
    pageTitle: PropTypes.string,
};

export default Navbar;