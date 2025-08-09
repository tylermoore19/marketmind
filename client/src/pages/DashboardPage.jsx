import { useState } from "react";
import { Toolbar, Tabs, Tab, Typography, Box } from "@mui/material";
import { useApiCall } from '../hooks/useApiCall';
import api from '../services/api';

const DashboardPage = () => {
    const [value, setValue] = useState(0);

    const handleChange = (event, newValue) => {
        setValue(newValue);
    };

    const callRoot = useApiCall(api.getRoot);

    // const handleCallBackend = async () => {
    //     const data = await callRoot();

    //     console.log('Backend response:', data);
    // };

    return (
        <Box sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}>
            <Toolbar>
                <Typography
                    variant="h6"
                    sx={{ flexGrow: 1, fontWeight: "bold", cursor: "pointer" }}
                >
                    MyApp
                </Typography>

                {/* Tabs on the right */}
                <Tabs
                    value={value}
                    onChange={handleChange}
                    textColor="inherit"
                    indicatorColor="secondary"
                >
                    <Tab label="Home" />
                    <Tab label="About" />
                    <Tab label="Services" />
                    <Tab label="Contact" />
                </Tabs>
            </Toolbar>
        </Box>
    );
};

export default DashboardPage;
