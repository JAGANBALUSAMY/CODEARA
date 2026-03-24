import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Levels from './pages/Levels'
import Practice from './pages/Practice'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <div>
      <Navbar />
      <div className="container" style={{ padding: '40px 24px' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/levels" element={<Levels />} />
          <Route path="/practice/:levelId" element={<Practice />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
