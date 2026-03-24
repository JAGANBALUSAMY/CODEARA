import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

function Dashboard() {
  const [progress, setProgress] = useState(null)
  const [attempts, setAttempts] = useState([])
  const [levels, setLevels] = useState([])
  const [dailyTask, setDailyTask] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [progressRes, attemptsRes, levelsRes, dailyRes] = await Promise.all([
        api.getProgress(),
        api.getRecentAttempts(10),
        api.getLevels(),
        api.getDailyTask().catch(() => ({ data: null }))
      ])
      setProgress(progressRes.data)
      setAttempts(attemptsRes.data)
      setLevels(levelsRes.data)
      if (dailyRes.data) setDailyTask(dailyRes.data)
    } catch (err) {
      console.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  const completedCount = progress?.levels_completed?.length || 0

  return (
    <div>
      <h1 className="page-title">Your Progress</h1>
      <p className="page-subtitle">Track your learning journey</p>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{progress?.attempts || 0}</div>
          <div className="stat-label">Total Attempts</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{progress?.successful_attempts || 0}</div>
          <div className="stat-label">Successful</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{Math.round(progress?.accuracy || 0)}%</div>
          <div className="stat-label">Accuracy</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{completedCount}/{levels.length}</div>
          <div className="stat-label">Levels Completed</div>
        </div>
      </div>

      {dailyTask && dailyTask.level && (
        <div className="card mb-32 daily-task-card" style={{ borderColor: 'var(--warning)', background: 'rgba(245, 158, 11, 0.05)' }}>
          <div className="flex flex-between align-center">
            <div>
              <span className="daily-task-badge" style={{ background: 'var(--warning)', color: '#000' }}>🌟 Daily Reinforcement Task</span>
              <h3 className="problem-title m-0 mt-20">{dailyTask.level.title}</h3>
              <p className="text-gray mt-20">We identified this as your weakest area based on your accuracy and attempt history. Master this to close your knowledge gap!</p>
            </div>
            <button 
              className="btn btn-primary" 
              style={{ background: 'var(--warning)', color: '#000' }}
              onClick={() => navigate(`/practice/${dailyTask.level_id}`)}
            >
              Practice Now
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-2 gap-20">
        <div className="card">
          <h3 className="problem-title mb-20">Levels Progress</h3>
          {levels.map((level) => {
            const isCompleted = progress?.levels_completed?.includes(level.id)
            return (
              <div 
                key={level.id}
                className="result-item"
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/practice/${level.id}`)}
              >
                <div className="flex flex-between">
                  <span>{level.title}</span>
                  <span className={`result-status ${isCompleted ? 'status-passed' : 'status-failed'}`}>
                    {isCompleted ? '✓ Completed' : '○ Not started'}
                  </span>
                </div>
              </div>
            )
          })}
        </div>

        <div className="card">
          <h3 className="problem-title mb-20">Recent Attempts</h3>
          {attempts.length === 0 ? (
            <p className="problem-text">No attempts yet. Start practicing!</p>
          ) : (
            attempts.map((attempt) => (
              <div key={attempt.id} className="result-item">
                <div className="flex flex-between">
                  <span className="result-value">{attempt.level_id}</span>
                  <span className={`result-status ${attempt.result === 'passed' ? 'status-passed' : 'status-failed'}`}>
                    {attempt.result}
                  </span>
                </div>
                <div className="input-label mt-20">
                  {new Date(attempt.timestamp).toLocaleString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {progress?.last_practiced && (
        <div className="card mt-20">
          <p className="problem-text">
            Last practiced: {new Date(progress.last_practiced).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  )
}

export default Dashboard
