import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // 预留Python后端接口
  timeout: 10000,
});

export const getDriverStandings = () => api.get('/driver-standings');
export const getConstructorStandings = () => api.get('/constructor-standings');
export const getAvailableYears = () => api.get('/available-years');
export const getRaceSchedule = (year) => api.get('/race-schedule', { params: { year } });
export const getNextRace = (year) => api.get('/next-race', { params: { year } });
export const getRaceWeekendSchedule = (year, round) => api.get('/race-weekend-schedule', { params: { year, round } });
export const getCircuitInfo = (year, round) => api.get('/circuit-info', { params: { year, round } });
// ... 其他接口

export default api; 