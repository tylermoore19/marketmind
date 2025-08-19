/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect, useCallback } from "react";
import { useAuth } from '../context/AuthContext';
import { useAlert } from '../context/AlertContext';
import { ApiResponse } from '@/types';

// Custom error for token expiration/invalid
export class TokenExpiredError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'TokenExpiredError';
    }
}

interface ApiCallState<T> {
    data: T | null;
    loading: boolean;
    message: string | null;
    error: string | null;
    fetch: (...args: any[]) => Promise<void>;
}

export function useApiCall<T>(apiFunc: (...args: any[]) => Promise<ApiResponse>, skipInitial = false, args = [], deps = []): ApiCallState<T> {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    const { logout, setToken } = useAuth();
    const { showAlert } = useAlert();

    const fetchData = useCallback(async (...args: any[]) => {
        setLoading(true);
        setError(null);
        setData(null);

        try {
            // Expect apiFunc to return an object: { data, refreshToken }
            const result: ApiResponse = await apiFunc(...args);
            if (result?.refreshToken) {
                setToken(result.refreshToken);
            }
            if (result?.message) {
                setMessage(result.message);
            }

            setData(result?.data as T);
        } catch (err: any) {
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

    return { data, loading, message, error, fetch: fetchData };
}
