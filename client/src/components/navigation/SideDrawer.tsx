/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect } from "react";
import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, IconButton, Box } from "@mui/material";
import { ChevronLeft, ChevronRight, Dashboard, ShowChart, SportsFootball } from "@mui/icons-material";
import { useNavigate, useLocation } from 'react-router-dom';
import logo from '../../assets/logo.png';

const tabs = [
    { text: "Dashboard", icon: <Dashboard /> },
    { text: "Stocks", icon: <ShowChart /> },
    { text: "Sports", icon: <SportsFootball /> },
];

interface Props {
    setPageTitle: (title: string) => void;
}

const SideDrawer = ({ setPageTitle }: Props) => {
    const [selectedTab, setSelectedTab] = useState(-1);
    const [open, setOpen] = useState(true);

    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const currentPath = location.pathname;
        const activeTab = tabs.findIndex(tab => `/${tab.text.toLowerCase()}` === currentPath);
        setSelectedTab(activeTab);
        setPageTitle(tabs[activeTab]?.text || "");
    }, [location.pathname]);

    const toggleDrawer = () => {
        setOpen(!open);
    };

    const tabClick = (idx: number) => {
        navigate(`/${tabs[idx].text.toLowerCase()}`);
    };

    return (
        <Drawer
            variant="permanent"
            open={open}
            sx={{
                position: 'relative',
                width: open ? 220 : 65,
                transition: "width 0.3s",
                "& .MuiDrawer-paper": {
                    width: 'inherit',
                    overflow: "visible",
                    backgroundColor: 'primary.main',
                    color: 'text.secondary'
                },
            }}
        >
            <Box sx={{ px: 2.5, py: 1.5, display: 'flex', justifyContent: 'center' }}>
                <img src={logo} alt="Logo" style={{ width: open ? 70 : 40, transition: 'width 0.3s ease-in-out' }} />
            </Box>
            {/* Sidebar Items */}
            <List sx={{ position: 'absolute', top: 90, width: '100%' }}>
                {tabs.map((item, index) => (
                    <ListItem key={item.text} sx={{ px: 1 }}>
                        <ListItemButton
                            sx={{
                                minHeight: 44,
                                justifyContent: open ? "initial" : "center",
                                px: 1.5,
                                py: 0,
                                "&.Mui-selected": {
                                    background: (theme) => theme.palette.gradients?.orange,
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

export default SideDrawer;