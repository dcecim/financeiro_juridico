import { useState, useRef, useEffect } from 'react';
import { useTheme, Theme } from '../contexts/ThemeContext';
import { Palette, Check, ChevronDown } from 'lucide-react';

const themes: { id: Theme; name: string; color: string; border?: string }[] = [
  { id: 'dark', name: 'Dark', color: '#1e293b' },
  { id: 'light', name: 'Light', color: '#ffffff', border: '#e2e8f0' },
  { id: 'emerald', name: 'Emerald Legal', color: '#064e3b' },
  { id: 'corporate', name: 'Corporate Blue', color: '#f0f9ff', border: '#bae6fd' },
  { id: 'midnight', name: 'Midnight Purple', color: '#2e1065' },
  { id: 'nordic', name: 'Nordic Gray', color: '#e5e7eb' },
  { id: 'sandstone', name: 'Sandstone', color: '#fffbeb' },
  { id: 'high-contrast', name: 'High Contrast', color: '#000000', border: '#ffff00' },
  { id: 'ocean', name: 'Ocean', color: '#083344' },
];

export const ThemeSelector = () => {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const currentTheme = themes.find(t => t.id === theme) || themes[0];

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-md bg-[var(--color-bg-paper)] hover:bg-opacity-80 transition-colors border border-[var(--color-border)] text-[var(--color-text-main)]"
      >
        <Palette className="w-5 h-5 text-[var(--color-primary)]" />
        <span className="hidden md:inline-block text-sm font-medium">{currentTheme.name}</span>
        <ChevronDown className="w-4 h-4 opacity-50" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-[var(--color-bg-paper)] ring-1 ring-black ring-opacity-5 z-50 max-h-96 overflow-y-auto border border-[var(--color-border)]">
          <div className="py-1" role="menu" aria-orientation="vertical">
            {themes.map((t) => (
              <button
                key={t.id}
                onClick={() => {
                  setTheme(t.id);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-4 py-3 text-sm flex items-center justify-between hover:bg-[var(--color-bg-main)] transition-colors ${
                  theme === t.id ? 'bg-[var(--color-bg-main)]' : ''
                }`}
                role="menuitem"
              >
                <div className="flex items-center">
                  <span
                    className="w-4 h-4 rounded-full mr-3 border"
                    style={{ 
                      backgroundColor: t.color, 
                      borderColor: t.border || 'transparent' 
                    }}
                  />
                  <span className="text-[var(--color-text-main)]">{t.name}</span>
                </div>
                {theme === t.id && (
                  <Check className="w-4 h-4 text-[var(--color-primary)]" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
