import { useState } from "react";
import { Toolbar, Tabs, Tab, Typography, Box } from "@mui/material";

const DashboardPage = () => {
    const [value, setValue] = useState(0);

    const handleChange = (event, newValue) => {
        setValue(newValue);
    };

    // const handleCallBackend = async () => {
    //     const data = await callRoot();

    //     console.log('Backend response:', data);
    // };

    return (
        <Box>
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
