import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

export type Theme = 
  | 'dark' 
  | 'light' 
  | 'emerald' 
  | 'corporate' 
  | 'midnight' 
  | 'nordic' 
  | 'sandstone' 
  | 'high-contrast' 
  | 'ocean';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Check localStorage first
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) return savedTheme;
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'dark'; // Default to dark as requested
  });

  useEffect(() => {
    const root = window.document.documentElement;
    
    // Remove old theme attributes if any (though we overwrite)
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
