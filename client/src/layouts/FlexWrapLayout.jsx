import { Box } from "@mui/material";
import PropTypes from 'prop-types';

const FlexWrapLayout = ({ children, styles = {} }) => (
    <Box
        sx={{
            display: 'flex',
            flexWrap: 'wrap',
            alignContent: 'flex-start',
            gap: { xs: 2, sm: 3, md: 4 },
            width: '100%',
            height: '100%',
            ...styles
        }}
    >
        {children}
    </Box>
);


FlexWrapLayout.propTypes = {
    children: PropTypes.node,
    styles: PropTypes.object,
};

export default FlexWrapLayout;