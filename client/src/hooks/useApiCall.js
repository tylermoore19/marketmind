/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect, useCallback } from "react";
import { useAuth } from '../context/AuthContext';
import { useAlert } from '../context/AlertContext';

// Custom error for token expiration/invalid
export class TokenExpiredError extends Error {
    constructor(message) {
        super(message);
        this.name = 'TokenExpiredError';
    }
}

export function useApiCall(apiFunc, skipInitial = false, args = [], deps = []) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const { logout, setToken } = useAuth();
    const { showAlert } = useAlert();

    const fetchData = useCallback(async (...args) => {
        setLoading(true);
        setError(null);
        setData(null);

        try {
            // Expect apiFunc to return an object: { data, refreshToken }
            const result = await apiFunc(...args);
            if (result && result.refreshToken) {
                setToken(result.refreshToken);
            }
            setData(result && result.data !== undefined ? result.data : result);
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
                showAlert('You have been signed out. You will be redirected to login page in 3 seconds...', 'error');
                setTimeout(() => {
                    logout();
                }, 4000);
            } else {
                setError(err.message || 'An error occurred');
            }
        } finally {
            setLoading(false);
        }
    }, deps);

    useEffect(() => {
        if (!skipInitial) {
            fetchData(...args);
        }
    }, [fetchData, skipInitial, ...args]);

    return { data, loading, error, fetch: fetchData };
}
