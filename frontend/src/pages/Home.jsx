import { useNavigate } from 'react-router-dom'

function Home() {
  const navigate = useNavigate()

  return (
    <div>
      <div className="hero">
        <h1 className="hero-title">Master Python Arrays</h1>
        <p className="hero-subtitle">
          Learn arrays through real code execution, test cases, and progressive challenges
        </p>
        <button 
          className="btn btn-primary" 
          style={{ padding: '14px 32px', fontSize: '16px' }}
          onClick={() => navigate('/levels')}
        >
          Start Learning
        </button>
      </div>

      <div className="topic-cards">
        <div className="topic-card" onClick={() => navigate('/levels')}>
          <div className="topic-icon">📊</div>
          <h3 className="topic-name">Arrays</h3>
          <p className="topic-description">
            Master array operations, searching, sorting, and more
          </p>
        </div>
      </div>
    </div>
  )
}

export default Home
