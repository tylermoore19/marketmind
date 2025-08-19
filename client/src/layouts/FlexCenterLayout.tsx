import { Box } from "@mui/material";
import { ReactNode } from 'react';

interface Props {
    children: ReactNode;
    styles: React.CSSProperties;
}

const FlexCenterLayout = ({ children, styles = {} }: Props) => (
    <Box
        sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: { xs: 2, sm: 3, md: 4 },
            width: '100%',
            height: '100%',
            ...styles
        }}
    >
        {children}
    </Box>
);

export default FlexCenterLayout;