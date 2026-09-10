import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

interface ThemeToggleProps {
  size?: 'sm' | 'md';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ size = 'md' }) => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
  const dim = size === 'sm' ? 30 : 34;

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      title={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      style={{
        width: dim,
        height: dim,
        borderRadius: 'var(--radius-full)',
        border: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface-alt)',
        color: 'var(--color-text-muted)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        flexShrink: 0,
        position: 'relative',
        overflow: 'hidden',
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-accent-border)';
        (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-accent)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-border)';
        (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-text-muted)';
      }}
    >
      {isDark ? <Moon size={size === 'sm' ? 14 : 16} /> : <Sun size={size === 'sm' ? 14 : 16} />}
    </button>
  );
};
