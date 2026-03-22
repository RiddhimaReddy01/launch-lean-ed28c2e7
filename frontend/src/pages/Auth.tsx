import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '@/components/layout/Nav';
import { useToast } from '@/hooks/use-toast';

type AuthMode = 'login' | 'signup';

// Supabase credentials from environment
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_KEY || '';

export default function Auth() {
  const [mode, setMode] = useState<AuthMode>('signup');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const logger = { error: console.error };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Call Supabase Auth endpoint
      const endpoint = `${SUPABASE_URL}/auth/v1/${mode === 'signup' ? 'signup' : 'token?grant_type=password'}`;

      const payload = {
        email,
        password,
        gotrue_meta_security: {},
      };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_KEY,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error_description || error.message || 'Authentication failed');
      }

      const data = await response.json();
      const token = data.session?.access_token || data.access_token;

      if (!token) {
        throw new Error('No access token received');
      }

      // Store JWT token
      localStorage.setItem('auth_token', token);
      localStorage.setItem('user_email', email);

      toast({
        title: 'Success!',
        description: `${mode === 'signup' ? 'Account created' : 'Logged in'} successfully`,
      });

      navigate('/research');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Authentication failed';
      logger.error('Auth error:', errorMsg);

      toast({
        title: 'Authentication Error',
        description: errorMsg,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    navigate('/');
  };

  return (
    <>
      <Nav onLogout={handleLogout} />
      <div
        className="flex items-center justify-center min-h-screen px-6"
        style={{ backgroundColor: 'var(--surface-bg)' }}
      >
        <div
          className="rounded-[16px] p-8 max-w-sm w-full"
          style={{ backgroundColor: 'var(--surface-card)', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
        >
          <h1 className="font-heading mb-2" style={{ fontSize: 24 }}>
            {mode === 'signup' ? 'Create account' : 'Sign in'}
          </h1>
          <p className="font-caption mb-8" style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
            {mode === 'signup'
              ? 'Join thousands validating their startup ideas'
              : 'Welcome back! Enter your credentials'}
          </p>

          <form onSubmit={handleAuth} className="flex flex-col gap-4">
            <div>
              <label
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 13,
                  fontWeight: 500,
                  color: 'var(--text-primary)',
                  display: 'block',
                  marginBottom: 6,
                }}
              >
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid var(--divider-light)',
                  borderRadius: 8,
                  fontSize: 14,
                  fontFamily: "'Inter', sans-serif",
                  backgroundColor: 'var(--surface-bg)',
                  color: 'var(--text-primary)',
                  outline: 'none',
                }}
                onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--accent-purple)')}
                onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--divider-light)')}
              />
            </div>

            <div>
              <label
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 13,
                  fontWeight: 500,
                  color: 'var(--text-primary)',
                  display: 'block',
                  marginBottom: 6,
                }}
              >
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid var(--divider-light)',
                  borderRadius: 8,
                  fontSize: 14,
                  fontFamily: "'Inter', sans-serif",
                  backgroundColor: 'var(--surface-bg)',
                  color: 'var(--text-primary)',
                  outline: 'none',
                }}
                onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--accent-purple)')}
                onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--divider-light)')}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !email || !password}
              style={{
                padding: '12px 16px',
                backgroundColor: 'var(--accent-purple)',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 500,
                fontFamily: "'Inter', sans-serif",
                cursor: 'pointer',
                opacity: isLoading || !email || !password ? 0.6 : 1,
              }}
            >
              {isLoading ? 'Loading...' : mode === 'signup' ? 'Create account' : 'Sign in'}
            </button>
          </form>

          <div style={{ marginTop: 24, textAlign: 'center' }}>
            <p className="font-caption" style={{ fontSize: 13, marginBottom: 12 }}>
              {mode === 'signup' ? 'Already have an account?' : "Don't have an account?"}
            </p>
            <button
              onClick={() => setMode(mode === 'signup' ? 'login' : 'signup')}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--accent-purple)',
                fontSize: 13,
                fontWeight: 500,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              {mode === 'signup' ? 'Sign in' : 'Sign up'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
