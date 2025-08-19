const BASE_URL = 'http://127.0.0.1:5000';

const handleResponse = async (response) => {
  const data = await response.json();

  // Check for refresh token in response headers
  const refreshToken = response.headers.get('X-Refresh-Token');

  if (!response.ok) {
    // Ensure error response has 'code' and 'message' properties if not present
    const safeData = {
      code: data && typeof data.code !== 'undefined' ? data.code : 'unknown_error',
      message: data && typeof data.message !== 'undefined' ? data.message : 'Request failed',
      ...data
    };
    const err = new Error(safeData.message);
    err.code = safeData.code;
    throw err;
  } else {
    // if api was successful, save current time as last activity
    localStorage.setItem('last_api_activity', Date.now().toString());
  }
  return { data, refreshToken };
}

const getAuthHeader = () => {
  const token = localStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  get: async (endpoint) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    });
    return handleResponse(response);
  },

  post: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  login: async (email, password) => {
    return api.post('/auth/login', { email, password });
  },

  register: async (email, password) => {
    return api.post('/auth/register', { email, password });
  },

  getTopStocks: async () => {
    return api.get('/stocks/top');
  },

  getTestingStocks: async () => {
    return api.get('/stocks/generate_content');
  },
};

export default api;