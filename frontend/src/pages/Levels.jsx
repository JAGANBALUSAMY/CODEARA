import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

function Levels() {
  const [levels, setLevels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dailyTask, setDailyTask] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchLevels()
    fetchDailyTask()
  }, [])

  const fetchLevels = async () => {
    try {
      const response = await api.getLevels()
      setLevels(response.data)
    } catch (err) {
      setError('Failed to load levels. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const fetchDailyTask = async () => {
    try {
      const response = await api.getDailyTask()
      setDailyTask(response.data)
    } catch (err) {
      console.error('Failed to load daily task')
    }
  }

  if (loading) {
    return <div className="loading">Loading levels...</div>
  }

  if (error) {
    return <div className="error-message">{error}</div>
  }

  return (
    <div>
      <h1 className="page-title">Array Practice</h1>
      <p className="page-subtitle">Choose a level to start practicing</p>

      {dailyTask && (
        <div className="card daily-task-card mb-32">
          <span className="daily-task-badge">Daily Challenge</span>
          <h3 className="level-title">{dailyTask.level?.title}</h3>
          <p className="problem-text">{dailyTask.level?.problem}</p>
          <button 
            className="btn btn-primary mt-20"
            onClick={() => navigate(`/practice/${dailyTask.level_id}`)}
          >
            Start Challenge
          </button>
        </div>
      )}

      <div className="grid grid-2">
        {levels.map((level) => (
          <div 
            key={level.id} 
            className="card level-card"
            onClick={() => navigate(`/practice/${level.id}`)}
          >
            <h3 className="level-title">{level.title}</h3>
            <span className={`level-difficulty difficulty-${level.difficulty}`}>
              {level.difficulty}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Levels
