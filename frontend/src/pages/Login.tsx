import { useState } from 'react'
import { ShieldCheck, Lock, User, KeyRound } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

export const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [show2FA, setShow2FA] = useState(false)
  
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      if (show2FA && !otpCode) {
        setError('Digite o código de autenticação')
        setLoading(false)
        return
      }
      
      await login(email, password, show2FA ? otpCode : undefined)
      navigate('/')
      
    } catch (err: any) {
      console.error(err)
      if (err.message === "2FA code required") {
        setShow2FA(true)
        setError('Autenticação de dois fatores necessária')
      } else if (err.message === "Invalid 2FA code") {
        setError('Código inválido')
      } else {
        setError(err.response?.data?.detail || 'Falha no login. Verifique suas credenciais.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-main)] transition-colors duration-300">
      <div className="bg-[var(--color-bg-paper)] p-8 rounded-lg shadow-md w-96 border border-[var(--color-border)]">
        <div className="flex justify-center mb-6">
          <ShieldCheck className="w-12 h-12 text-[var(--color-primary)]" />
        </div>
        <h2 className="text-2xl font-bold text-center text-[var(--color-text-main)] mb-6">Acesso ao Sistema</h2>
        {error && <div className={`mb-4 text-sm text-center p-2 rounded ${error.includes('necessária') ? 'bg-[var(--color-warning)]/10 text-[var(--color-warning)]' : 'bg-[var(--color-danger)]/10 text-[var(--color-danger)]'}`}>{error}</div>}
        
        <form className="space-y-4" onSubmit={handleLogin}>
          {!show2FA ? (
            <>
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-main)]">Email</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-[var(--color-text-muted)]" />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] block w-full pl-10 sm:text-sm border-[var(--color-border)] rounded-md p-2 border bg-[var(--color-bg-main)] text-[var(--color-text-main)] placeholder-[var(--color-text-muted)]"
                    placeholder="seu@email.com"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-main)]">Senha</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-[var(--color-text-muted)]" />
                  </div>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] block w-full pl-10 sm:text-sm border-[var(--color-border)] rounded-md p-2 border bg-[var(--color-bg-main)] text-[var(--color-text-main)] placeholder-[var(--color-text-muted)]"
                    placeholder="••••••••"
                  />
                </div>
              </div>
            </>
          ) : (
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-main)]">Código 2FA</label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <KeyRound className="h-5 w-5 text-[var(--color-text-muted)]" />
                </div>
                <input
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  required
                  className="focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] block w-full pl-10 sm:text-sm border-[var(--color-border)] rounded-md p-2 border bg-[var(--color-bg-main)] text-[var(--color-text-main)] placeholder-[var(--color-text-muted)]"
                  placeholder="000000"
                  autoFocus
                />
              </div>
              <p className="mt-2 text-xs text-[var(--color-text-muted)] text-center">
                Abra seu aplicativo autenticador e digite o código de 6 dígitos.
              </p>
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-[var(--color-primary-foreground)] bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--color-primary)] disabled:opacity-50 transition-colors"
          >
            {loading ? 'Entrando...' : (show2FA ? 'Confirmar' : 'Entrar')}
          </button>
          
          {show2FA && (
            <button
              type="button"
              onClick={() => { setShow2FA(false); setOtpCode(''); setError(''); }}
              className="w-full text-center text-sm text-[var(--color-primary)] hover:text-[var(--color-primary-hover)]"
            >
              Voltar para login
            </button>
          )}
        </form>
      </div>
    </div>
  )
}
