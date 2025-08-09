import { Box } from "@mui/material";
import PropTypes from 'prop-types';

const FlexCenterLayout = ({ children, styles = {} }) => (
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


FlexCenterLayout.propTypes = {
    children: PropTypes.node,
    styles: PropTypes.object,
};

export default FlexCenterLayout;