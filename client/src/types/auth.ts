export interface LoginResponse {
    token: string;
    user: {
        id: string;
        email: string;
    };
}

export interface SignupResponse {
    token: string;
}