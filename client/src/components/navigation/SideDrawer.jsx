import { useState } from "react";
import PropTypes from 'prop-types';
import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, IconButton, Box } from "@mui/material";
import { ChevronLeft, ChevronRight, Dashboard, ShowChart, SportsFootball } from "@mui/icons-material";
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/logo.png';

const tabs = [
    { text: "Dashboard", icon: <Dashboard /> },
    { text: "Stocks", icon: <ShowChart /> },
    { text: "Sports", icon: <SportsFootball /> },
];

const SideDrawer = ({ setPageTitle }) => {
    const [selectedTab, setSelectedTab] = useState(-1);
    const [open, setOpen] = useState(true);

    const navigate = useNavigate();

    const toggleDrawer = () => {
        setOpen(!open);
    };

    const tabClick = (idx) => {
        setSelectedTab(idx);
        const pageTitle = tabs[idx].text;
        setPageTitle(pageTitle);
        const newLink = pageTitle.toLowerCase();
        navigate(`/${newLink}`);
    };

    return (
        <Drawer
            variant="permanent"
            open={open}
            sx={{
                position: 'relative',
                width: open ? 240 : 65,
                transition: "width 0.3s",
                "& .MuiDrawer-paper": {
                    width: 'inherit',
                    overflow: "visible",
                    backgroundColor: 'primary.main',
                    color: 'text.secondary'
                },
            }}
        >
            <Box sx={{ px: 2.5, pt: 2, pb: 1, display: 'flex', justifyContent: 'center' }}>
                {open && <img src={logo} alt="Logo" style={{ width: 80 }} />}
            </Box>
            {/* Sidebar Items */}
            <List sx={{ position: 'absolute', top: 90, width: '100%' }}>
                {tabs.map((item, index) => (
                    <ListItem key={item.text} sx={{ p: 1 }}>
                        <ListItemButton
                            sx={{
                                minHeight: 44,
                                justifyContent: open ? "initial" : "center",
                                px: 1.5,
                                py: 0,
                                "&.Mui-selected": {
                                    background: (theme) => theme.palette.gradients.orange,
                                },
                                "&:hover": {
                                    textDecoration: "underline",
                                },
                                borderRadius: '10px'
                            }}
                            selected={selectedTab === index}
                            onClick={() => tabClick(index)}
                        >
                            <ListItemIcon
                                sx={{
                                    minWidth: 0,
                                    mr: open ? 3 : "auto",
                                    justifyContent: "center",
                                    '& .MuiSvgIcon-root': {
                                        color: theme => theme.palette.text.secondary,
                                    }
                                }}
                            >
                                {item.icon}
                            </ListItemIcon>
                            {open && <ListItemText primary={item.text} />}
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>

            {/* Arrow Button */}
            <Box
                sx={{
                    position: "absolute",
                    bottom: 50,
                    right: open ? -20 : -20, // adjust as needed, negative to move outside
                    width: 40,
                    height: 40,
                    bgcolor: "primary.main",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                    zIndex: 1300, // above drawer content
                    transition: "right 0.3s",
                    '& .MuiSvgIcon-root': {
                        color: theme => theme.palette.text.secondary,
                    }
                }}
            >
                <IconButton
                    onClick={toggleDrawer}
                    size="small"
                    sx={{ color: (theme) => theme.palette.primary.main }}
                >
                    {open ? <ChevronLeft /> : <ChevronRight />}
                </IconButton>
            </Box>
        </Drawer>
    );
};

SideDrawer.propTypes = {
    setPageTitle: PropTypes.func
};

export default SideDrawer;