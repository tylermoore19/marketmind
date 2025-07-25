import PropTypes from 'prop-types';

const AuthLayout = ({ children }) => {
    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {children}
            </main>
        </div>
    );
};

AuthLayout.propTypes = {
    children: PropTypes.node,
};

export default AuthLayout;
