import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

type AlertSeverity = 'success' | 'error' | 'info' | 'warning';

interface Alert {
    message: string;
    severity: AlertSeverity;
}

interface AlertContextType {
    alert: Alert | null;
    showAlert: (message: string, severity?: AlertSeverity) => void;
    hideAlert: () => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

interface Props {
    children: ReactNode;
}

export const AlertProvider = ({ children }: Props) => {
    const [alert, setAlert] = useState<Alert | null>(null);

    // Show alert with message and severity ('success', 'error', etc.)
    const showAlert = useCallback((message: string, severity: AlertSeverity = 'info') => {
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

export const useAlert = () => {
    const context = useContext(AlertContext);
    if (!context) {
        throw new Error('useAlert must be used within an AlertProvider');
    }
    return context;
};