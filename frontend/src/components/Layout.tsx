import { ShieldCheck, LayoutDashboard, FileText, Wallet, Users, Tags } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { Link, useLocation } from 'react-router-dom'
import { ThemeSelector } from './ThemeSelector'

export const Layout = ({ children }: { children: React.ReactNode }) => {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path 
      ? "bg-[var(--color-primary)]/10 text-[var(--color-primary)]" 
      : "text-[var(--color-text-muted)] hover:bg-[var(--color-bg-main)] hover:text-[var(--color-text-main)]"
  }

  return (
    <div className="flex h-screen bg-[var(--color-bg-main)] transition-colors duration-300">
      {/* Sidebar */}
      <div className="w-64 bg-[var(--color-bg-paper)] shadow-lg flex-shrink-0 border-r border-[var(--color-border)] transition-colors duration-300">
        <div className="h-16 flex items-center px-6 border-b border-[var(--color-border)]">
          <ShieldCheck className="w-8 h-8 text-[var(--color-primary)] mr-2" />
          <span className="text-lg font-bold text-[var(--color-text-main)]">Financeiro Jurídico</span>
        </div>
        <nav className="mt-6 px-4 space-y-2">
          <Link to="/" className={`flex items-center px-4 py-2 rounded-md transition-colors ${isActive('/')}`}>
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Dashboard
          </Link>
          <Link to="/processos" className={`flex items-center px-4 py-2 rounded-md transition-colors ${isActive('/processos')}`}>
            <FileText className="w-5 h-5 mr-3" />
            Processos
          </Link>
          <Link to="/participantes" className={`flex items-center px-4 py-2 rounded-md transition-colors ${isActive('/participantes')}`}>
            <Users className="w-5 h-5 mr-3" />
            Participantes
          </Link>
          <Link to="/financeiro" className={`flex items-center px-4 py-2 rounded-md transition-colors ${isActive('/financeiro')}`}>
            <Wallet className="w-5 h-5 mr-3" />
            Financeiro
          </Link>
          <Link to="/centros-custo" className={`flex items-center px-4 py-2 rounded-md transition-colors ${isActive('/centros-custo')}`}>
            <Tags className="w-5 h-5 mr-3" />
            Centros de Custo
          </Link>
        </nav>
      </div>
      
      {/* Content */}
      <div className="flex-1 flex flex-col overflow-hidden bg-[var(--color-bg-main)] transition-colors duration-300">
        <header className="h-16 bg-[var(--color-bg-paper)] shadow-sm flex items-center justify-between px-8 flex-shrink-0 z-10 border-b border-[var(--color-border)] transition-colors duration-300">
          <h1 className="text-xl font-semibold text-[var(--color-text-main)]">
            {location.pathname === '/' ? 'Visão Geral' : 
             location.pathname === '/processos' ? 'Gestão de Processos' :
             location.pathname === '/participantes' ? 'Gestão de Participantes' :
             location.pathname === '/financeiro' ? 'Gestão Financeira' : 
             location.pathname === '/centros-custo' ? 'Gestão de Centros de Custo' : 'Sistema'}
          </h1>
          <div className="flex items-center space-x-6">
            <ThemeSelector />
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-right">
                  <p className="font-medium text-[var(--color-text-main)]">{user?.email}</p>
                  <button onClick={logout} className="text-xs text-[var(--color-danger)] hover:opacity-80">Sair</button>
              </div>
              <div className="w-8 h-8 bg-[var(--color-primary)]/20 rounded-full flex items-center justify-center text-[var(--color-primary)] font-bold uppercase">
                {user?.email?.substring(0, 2) || 'US'}
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-8 bg-[var(--color-bg-main)] transition-colors duration-300">
          {children}
        </main>
      </div>
    </div>
  )
}
