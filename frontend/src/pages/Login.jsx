import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api, { apiMessage } from '../services/api.js'
import Field from '../components/Field.jsx'
export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' }); const [error, setError] = useState(''); const [loading, setLoading] = useState(false); const navigate = useNavigate()
  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })
  const submit = async (e) => { e.preventDefault(); setError(''); setLoading(true); try { const { data } = await api.post('/auth/login', form); localStorage.setItem('token', data.access_token); const me = await api.get('/auth/me'); localStorage.setItem('user', JSON.stringify(me.data)); navigate('/', { replace: true }) } catch (err) { setError(apiMessage(err)) } finally { setLoading(false) } }
  return <main className="auth-shell"><form className="panel auth-panel" onSubmit={submit}><p className="eyebrow">CAMPUSDESK</p><h1>Welcome back</h1><p className="muted">Sign in to manage your students and courses.</p>{error && <div className="alert">{error}</div>}<Field label="Email address" name="email" type="email" autoComplete="email" value={form.email} onChange={change} required /><Field label="Password" name="password" type="password" autoComplete="current-password" value={form.password} onChange={change} required /><button className="button button-primary full" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button><p className="auth-switch">New here? <Link to="/register">Create an account</Link></p></form></main>
}
