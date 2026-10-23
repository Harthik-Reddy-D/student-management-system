import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api, { apiMessage } from '../services/api.js'
import Field from '../components/Field.jsx'
export default function Register() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '' }); const [error, setError] = useState(''); const [loading, setLoading] = useState(false); const navigate = useNavigate()
  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })
  const submit = async (e) => { e.preventDefault(); setError(''); if (form.password.length < 8) { setError('Password must contain at least 8 characters.'); return } setLoading(true); try { await api.post('/auth/register', form); const { data } = await api.post('/auth/login', { email: form.email, password: form.password }); localStorage.setItem('token', data.access_token); navigate('/', { replace: true }) } catch (err) { setError(apiMessage(err)) } finally { setLoading(false) } }
  return <main className="auth-shell"><form className="panel auth-panel" onSubmit={submit}><p className="eyebrow">CAMPUSDESK</p><h1>Create your account</h1><p className="muted">Get started with student management.</p>{error && <div className="alert">{error}</div>}<Field label="Full name" name="full_name" value={form.full_name} onChange={change} minLength="2" required /><Field label="Email address" name="email" type="email" value={form.email} onChange={change} required /><Field label="Password (8+ characters)" name="password" type="password" value={form.password} onChange={change} minLength="8" required /><button className="button button-primary full" disabled={loading}>{loading ? 'Creating account…' : 'Create account'}</button><p className="auth-switch">Already registered? <Link to="/login">Sign in</Link></p></form></main>
}
