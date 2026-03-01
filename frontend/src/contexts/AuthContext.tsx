import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '../services/auth';
import { User, LoginResponse } from '../services/types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string, otpCode?: string) => Promise<void>;
  logout: () => void;
  requires2FA: boolean;
  clear2FA: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [requires2FA, setRequires2FA] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // Verify token validity by fetching profile
          const userProfile = await authService.getProfile();
          setUser(userProfile);
          setIsAuthenticated(true);
        } catch (error) {
          console.error("Token invalid or expired", error);
          localStorage.removeItem('token');
          setIsAuthenticated(false);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string, otpCode?: string) => {
    try {
      setRequires2FA(false);
      const response: LoginResponse = await authService.login(username, password, otpCode);
      
      localStorage.setItem('token', response.access_token);
      
      // Fetch user profile after successful login
      const userProfile = await authService.getProfile();
      setUser(userProfile);
      setIsAuthenticated(true);
      
    } catch (error: any) {
      // Check if error is due to missing 2FA code
      if (error.response?.status === 401 && error.response?.data?.detail === "2FA code required") {
        setRequires2FA(true);
        throw new Error("2FA code required"); // Signal to UI to show OTP input
      } else if (error.response?.status === 401 && error.response?.data?.detail === "Invalid 2FA code") {
         setRequires2FA(true); // Keep showing OTP input
         throw new Error("Invalid 2FA code");
      }
      
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    setRequires2FA(false);
    // Force reload to clear any in-memory state if needed, or just redirect
    window.location.href = '/login';
  };

  const clear2FA = () => {
    setRequires2FA(false);
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      isAuthenticated, 
      isLoading, 
      login, 
      logout,
      requires2FA,
      clear2FA
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
