import axios from "axios";

// 1. Establish the centralized backend connection gateway mapping to Vite's proxy port
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// 2. Interceptor hook to dynamically inject the active JWT session token into outward calls
api.interceptors.request.use(
    (config) => {
        // FIXED: Lowercase 'token' to match your Login storage call keys perfectly
        const activeToken = localStorage.getItem('token');
        
        if (activeToken) {
            // FIXED: Removed the trailing semicolon inside the template literal string
            config.headers.Authorization = `Bearer ${activeToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;