import { NavLink, useNavigate } from 'react-router-dom'
export default function Navbar() {
  const navigate = useNavigate()
  const logout = () => { localStorage.removeItem('token'); localStorage.removeItem('user'); navigate('/login', { replace: true }) }
  return <header className="navbar"><NavLink className="brand" to="/">CampusDesk</NavLink><nav><NavLink to="/">Dashboard</NavLink><NavLink to="/students">Students</NavLink><NavLink to="/courses">Courses</NavLink></nav><button className="button button-ghost" onClick={logout}>Log out</button></header>
}
