import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();
  const { user, profile, signOut } = useAuth();

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
      <Link to="/" style={{ fontSize: 18, textDecoration: 'none', color: 'inherit' }}>
        <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Launch</span>
        <span style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic', fontWeight: 400 }}>Lens</span>
      </Link>

      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/research')}
          className="text-sm"
          style={{ fontFamily: "'Inter', sans-serif", fontWeight: 300, color: 'var(--text-link)', background: 'none', border: 'none', cursor: 'pointer' }}
        >
          New idea
        </button>

        {user ? (
          <>
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
          </>
        ) : (
          <button
            onClick={() => navigate('/auth')}
            className="text-sm"
            style={{ fontFamily: "'Inter', sans-serif", fontWeight: 300, color: 'var(--text-link)', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            Log in
          </button>
        )}
      </div>
    </nav>
  );
}
