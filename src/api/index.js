import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // 预留Python后端接口
  timeout: 10000,
});

export const getDashboardData = () => api.get('/dashboard');
export const getDriverStandings = () => api.get('/driver-standings');
export const getConstructorStandings = () => api.get('/constructor-standings');
// ... 其他接口

export default api; 