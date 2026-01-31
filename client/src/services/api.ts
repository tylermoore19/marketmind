import { ApiResponse, ErrorResponse, LoginResponse, SignupResponse } from '@/types';

const BASE_URL = 'http://127.0.0.1:5050';

interface ApiError extends Error {
  code: string;
}

const handleResponse = async <T = any>(response: Response): Promise<ApiResponse<T>> => {
  const data = await response.json();

  // Check for refresh token in response headers
  const refreshToken = response.headers.get('X-Refresh-Token');

  if (!response.ok) {
    const { code, message, ...rest } = data as ErrorResponse;

    const safeCode = typeof code === 'string' ? code : 'unknown_error';
    const safeMessage = typeof message === 'string' ? message : 'Request failed';

    const err = new Error(safeMessage) as ApiError;
    err.code = safeCode;

    // Attach full error payload to the error object
    Object.assign(err, rest);

    throw err;
  } else {
    // if api was successful, save current time as last activity
    localStorage.setItem('last_api_activity', Date.now().toString());
  }

  return { ...data, refreshToken };
}

const getAuthHeader = () => {
  const token = localStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  get: async <T = any>(endpoint: string): Promise<ApiResponse<T>> => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      } as HeadersInit,
    });

    return handleResponse<T>(response);
  },

  post: async <T = any>(endpoint: string, data: any): Promise<ApiResponse<T>> => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      } as HeadersInit,
      body: JSON.stringify(data),
    });

    return handleResponse<T>(response);
  },

  login: async (email: string, password: string): Promise<ApiResponse<LoginResponse>> => {
    return api.post('/auth/login', { email, password });
  },

  register: async (email: string, password: string): Promise<ApiResponse<SignupResponse>> => {
    return api.post('/auth/register', { email, password });
  },

  getTopStocks: async (): Promise<ApiResponse<any>> => {
    return api.get('/stocks/top');
  },

  getBullishStocks: async (): Promise<ApiResponse<any>> => {
    return api.get('/stocks/bullish');
  },

  getBearishStocks: async (): Promise<ApiResponse<any>> => {
    return api.get('/stocks/bearish');
  },

  getSportsPredictions: async (): Promise<ApiResponse<any>> => {
    return api.get('/sports/predictions');
  },

  getSportsParlay: async (): Promise<ApiResponse<any>> => {
    return api.get('/sports/parlay');
  },
};

export default api;