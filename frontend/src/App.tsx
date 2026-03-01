import { ReactElement } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { Processos } from './pages/Processos'
import { Financeiro } from './pages/Financeiro'
import { Participantes } from './pages/Participantes'
import CentrosCusto from './pages/CentrosCusto'
import { PrivateRoute } from './components/PrivateRoute'

// Componente para redirecionar se já estiver logado
const PublicRoute = ({ children }: { children: ReactElement }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div className="h-screen flex items-center justify-center">Carregando...</div>;
  }
  
  return isAuthenticated ? <Navigate to="/" /> : children;
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Router>
          <Routes>
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } 
          />
          
          <Route element={<PrivateRoute />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/processos" element={<Processos />} />
            <Route path="/financeiro" element={<Financeiro />} />
            <Route path="/participantes" element={<Participantes />} />
            <Route path="/centros-custo" element={<CentrosCusto />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  )
}

export default App
