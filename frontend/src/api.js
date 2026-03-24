import axios from 'axios'

const API_BASE = 'http://localhost:8000'

export const api = {
  getLevels: () => axios.get(`${API_BASE}/levels`),
  
  getLevel: (levelId) => axios.get(`${API_BASE}/levels/${levelId}`),
  
  executeCode: (code, levelId) => 
    axios.post(`${API_BASE}/execute`, { code, level_id: levelId }),
  
  submitCode: (code, levelId, passed, failedCases) =>
    axios.post(`${API_BASE}/submit`, {
      code,
      level_id: levelId,
      passed,
      failed_cases: failedCases
    }),
  
  getProgress: () => axios.get(`${API_BASE}/progress`),
  
  getDailyTask: () => axios.get(`${API_BASE}/daily-task`),
  
  getRecentAttempts: (limit = 10) => 
    axios.get(`${API_BASE}/attempts?limit=${limit}`),
    
  getFeedback: (code, error, expected, actual) =>
    axios.post(`${API_BASE}/feedback`, {
      user_code: code,
      error_message: error,
      expected_output: expected,
      actual_output: actual
    })
}
