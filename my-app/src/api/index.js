import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
});

export const getDriverStandings = () => api.get('/driver-standings');
export const getConstructorStandings = () => api.get('/constructor-standings');
export const getAvailableYears = () => api.get('/available-years');
export const getRaceSchedule = (year) => api.get('/race-schedule', { params: { year } });
export const getNextRace = (year) => api.get('/next-race', { params: { year } });
export const getRaceWeekendSchedule = (year, round) => api.get('/race-weekend-schedule', { params: { year, round } });
export const getCircuitInfo = (year, round) => api.get('/circuit-info', { params: { year, round } });

// Results API
export const getRaceResults = (year, round) => api.get('/race-results', { params: { year, round } });
export const getQualifyingResults = (year, round) => api.get('/qualifying-results', { params: { year, round } });
export const getPracticeResults = (year, round, session) => api.get('/practice-results', { params: { year, round, session } });
export const getRaceSummary = (year, round) => api.get('/race-summary', { params: { year, round } });
export const getAvailableSessions = (year, round) => api.get('/race-summary', { params: { year, round } });
export const getRaceHighlights = (year, round) => api.get('/race-highlights', { params: { year, round } });

export default api; 