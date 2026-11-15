import axios from 'axios';

const rawBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const normalizedBaseUrl = rawBaseUrl.endsWith('/api')
  ? rawBaseUrl
  : `${rawBaseUrl.replace(/\/+$/, '')}/api`;

const api = axios.create({
  baseURL: normalizedBaseUrl,
});

// Automatically handle Content-Type for JSON vs FormData
api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    // Delete explicit Content-Type so browser can add multipart/form-data with proper boundary
    if (config.headers) {
      if (typeof config.headers.delete === 'function') {
        config.headers.delete('content-type');
        config.headers.delete('Content-Type');
      }
      delete (config.headers as any)['content-type'];
      delete (config.headers as any)['Content-Type'];
    }
  } else if (config.headers) {
    const hasContentType =
      (typeof config.headers.has === 'function' && config.headers.has('content-type')) ||
      (config.headers as any)['content-type'] ||
      (config.headers as any)['Content-Type'];
    if (!hasContentType) {
      if (typeof config.headers.set === 'function') {
        config.headers.set('Content-Type', 'application/json');
      } else {
        (config.headers as any)['Content-Type'] = 'application/json';
      }
    }
  }
  return config;
});

export default api;
