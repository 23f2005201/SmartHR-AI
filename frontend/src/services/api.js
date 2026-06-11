import axios from "axios";

const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

//Interceptor hook to inject the current active session token into headers
api.interceptors.request.use(
    (config) => {
        const activeToken = localStorage.getItem('Token');
        if (activeToken) {
            config.headers.Authorization = `Bearer ${activeToken};`
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;
