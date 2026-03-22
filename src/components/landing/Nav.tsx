import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();
  const { user, profile } = useAuth();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const displayName = profile?.display_name || user?.email?.split('@')[0] || '';
  const initials = displayName.slice(0, 2).toUpperCase();

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 transition-all duration-200"
      style={{
        height: 64,
        backgroundColor: scrolled ? 'rgba(250,250,248,0.9)' : 'transparent',
        backdropFilter: scrolled ? 'blur(12px)' : 'none',
      }}
    >
      <span style={{ fontSize: 18, cursor: 'pointer' }} onClick={() => navigate('/')}>
        <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Launch </span>
        <span style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic', fontWeight: 400 }}>LEAN</span>
      </span>

      {user ? (
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-sm"
            style={{ fontFamily: "'Inter', sans-serif", fontWeight: 300, color: 'var(--text-link)', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            Saved
          </button>
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-medium cursor-pointer"
            style={{ backgroundColor: 'var(--accent-purple)', color: '#fff' }}
            onClick={() => navigate('/dashboard')}
            title={displayName}
          >
            {initials}
          </div>
        </div>
      ) : (
        <button
          onClick={() => navigate('/auth')}
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 300,
            color: '#6B6B6B',
            cursor: 'pointer',
            background: 'none',
            border: 'none',
          }}
        >
          Log in
        </button>
      )}
    </nav>
  );
}
