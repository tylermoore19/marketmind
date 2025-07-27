const BASE_URL = 'http://127.0.0.1:5000';

const handleResponse = async (response) => {
  const data = await response.json();
  console.log('data', data)
  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }
  return data;
}

export const api = {
  get: async (endpoint) => {
    const response = await fetch(`${BASE_URL}${endpoint}`);
    return handleResponse(response);
  },

  post: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
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
};

export default api;