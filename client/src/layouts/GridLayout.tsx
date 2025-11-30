import { Grid2, Stack } from "@mui/material";
import { ReactNode } from 'react';

interface Props {
    children: ReactNode;
    styles?: React.CSSProperties;
}

// TODO : need to figure out how to use the padding object for the spacing here as well

const GridLayoutTesting = () => (
    <Grid2 container spacing={{ lg: 2 }} width="100%" height="100%">
        <Grid2 size={4}>
            <Stack spacing={4} sx={{ border: '1px solid black' }}>
                <div style={{ border: '1px solid black', minHeight: '33%' }}>hello</div>
                <div style={{ border: '1px solid black', height: '33%' }}>hello</div>
                <div style={{ border: '1px solid black', height: '33%' }}>hello</div>
            </Stack>
        </Grid2>
        <Grid2 size={8} sx={{ border: '1px solid black' }}>
            <div style={{ height: '100%', boxSizing: 'border-box' }}>
                testing testing
            </div>
        </Grid2>
    </Grid2>
);

export default GridLayoutTesting;