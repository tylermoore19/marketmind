/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect } from "react";
import { Toolbar, Typography, Box } from "@mui/material";
import { useApiCall } from '../hooks/useApiCall';
import { useAlert } from '../context/AlertContext';
import api from '../services/api';

const StocksPage = () => {
    const [data, setData] = useState(null);
    const callTopStocks = useApiCall(api.getTopStocks);
    const { showAlert } = useAlert();

    useEffect(() => {
        const fetchStocks = async () => {
            try {
                const stocks = await callTopStocks();
                setData(stocks);
            } catch (error) {
                showAlert(error.message, "error");
            }
        };

        fetchStocks();
    }, []);

    return (
        <Box>
            <Toolbar>
                <Typography
                    variant="h6"
                    sx={{ flexGrow: 1, fontWeight: "bold", cursor: "pointer" }}
                >
                    Stocks
                </Typography>

                {/* Tabs on the right */}
                {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
            </Toolbar>
        </Box>
    )
};

export default StocksPage;