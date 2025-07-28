import { createContext, useContext, useState, useCallback } from 'react';
import PropTypes from 'prop-types';

const AlertContext = createContext();

export const AlertProvider = ({ children }) => {
    const [alert, setAlert] = useState(null);

    // Show alert with message and severity ('success', 'error', etc.)
    const showAlert = useCallback((message, severity = 'info') => {
        setAlert({ message, severity });
        // Optionally auto-hide after a few seconds:
        const timeoutInterval = severity !== 'error' ? 4000 : 9000;
        setTimeout(() => setAlert(null), timeoutInterval);
    }, []);

    // Hide alert manually
    const hideAlert = useCallback(() => setAlert(null), []);

    return (
        <AlertContext.Provider value={{ alert, showAlert, hideAlert }}>
            {children}
        </AlertContext.Provider>
    );
};

AlertProvider.propTypes = {
    children: PropTypes.node.isRequired,
};

export const useAlert = () => {
    const context = useContext(AlertContext);
    if (!context) {
        throw new Error('useAlert must be used within an AlertProvider');
    }
    return context;
};