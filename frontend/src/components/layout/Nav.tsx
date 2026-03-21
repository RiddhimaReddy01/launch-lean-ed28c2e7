import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface NavProps {
  onLogout?: () => void;
}

export default function Nav({ onLogout }: NavProps) {
  const [scrolled, setScrolled] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('auth_token');
    setIsAuthenticated(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    setIsAuthenticated(false);
    onLogout?.();
    navigate('/');
  };

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 transition-all duration-200"
      style={{
        height: 64,
        backgroundColor: scrolled ? 'rgba(250,250,248,0.9)' : 'transparent',
        backdropFilter: scrolled ? 'blur(12px)' : 'none'
      }}>

      <Link to="/" style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>
        <span style={{ fontSize: 18 }}>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Launch </span>
          <span style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic', fontWeight: 400 }}>​LEAN</span>
        </span>
      </Link>

      <div className="flex items-center gap-6">
        {isAuthenticated ? (
          <>
            <span
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                fontWeight: 400,
                color: 'var(--text-muted)',
              }}
            >
              {localStorage.getItem('user_email')}
            </span>
            <button
              onClick={handleLogout}
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 14,
                fontWeight: 300,
                color: '#6B6B6B',
                cursor: 'pointer',
                background: 'none',
                border: 'none',
                padding: 0,
              }}
            >
              Log out
            </button>
          </>
        ) : (
          <span
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 12,
              fontWeight: 300,
              color: 'var(--text-muted)',
            }}
          >
            Exploring (signup to save)
          </span>
        )}
      </div>
    </nav>
  );
}
