import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="container navbar-content">
        <Link to="/" className="logo">Codara</Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/levels" className="nav-link">Practice</Link>
          <Link to="/dashboard" className="nav-link">Dashboard</Link>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
