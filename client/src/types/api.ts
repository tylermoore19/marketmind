export interface ApiResponse<T = any> {
    refreshToken?: string | null;
    message?: string;
    data: T;
}

export interface ErrorResponse {
    code?: string;
    message?: string;
    [key: string]: any; // support extra fields
}