import { useAuth } from '../context/AuthContext';
import { useAlert } from '../context/AlertContext';

// Custom error for token expiration/invalid
export class TokenExpiredError extends Error {
    constructor(message) {
        super(message);
        this.name = 'TokenExpiredError';
    }
}

export function useApiCall(apiFunc) {
    const { logout } = useAuth();
    const { showAlert } = useAlert();

    return async (...args) => {
        try {
            return await apiFunc(...args);
        } catch (err) {
            // if it's an authentication issue, log out the user. otherwise, rethrow the error and let the individual component handle it
            if (
                err instanceof TokenExpiredError ||
                (err && err.code && (
                    err.code.includes('token_expired') ||
                    err.code.includes('authorization_required') ||
                    err.code.includes('invalid_token')
                ))
            ) {
                logout();
                showAlert('You have been signed out. Please log in again.', 'info');
            } else {
                throw err;
            }
        }
    };
}
