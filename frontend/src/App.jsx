import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Students from './pages/Students.jsx'
import StudentForm from './pages/StudentForm.jsx'
import Courses from './pages/Courses.jsx'
function Layout({ children }) { return <><Navbar />{children}</> }
export default function App() {
  return <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route path="/" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
    <Route path="/students" element={<ProtectedRoute><Layout><Students /></Layout></ProtectedRoute>} />
    <Route path="/students/new" element={<ProtectedRoute><Layout><StudentForm /></Layout></ProtectedRoute>} />
    <Route path="/students/:id/edit" element={<ProtectedRoute><Layout><StudentForm /></Layout></ProtectedRoute>} />
    <Route path="/courses" element={<ProtectedRoute><Layout><Courses /></Layout></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
}
