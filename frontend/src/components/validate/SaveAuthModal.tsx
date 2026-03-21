import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';

interface SaveAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveSuccess?: () => void;
}

type AuthMode = 'login' | 'signup';

export default function SaveAuthModal({ isOpen, onClose, onSaveSuccess }: SaveAuthModalProps) {
  const [mode, setMode] = useState<AuthMode>('signup');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  if (!isOpen) return null;

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Call real Supabase Auth endpoint
      const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
      const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_KEY || '';

      const endpoint = `${SUPABASE_URL}/auth/v1/${mode === 'signup' ? 'signup' : 'token?grant_type=password'}`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_KEY,
        },
        body: JSON.stringify({ email, password }),
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

      localStorage.setItem('auth_token', token);
      localStorage.setItem('user_email', email);

      toast({
        title: 'Success!',
        description: `${mode === 'signup' ? 'Account created' : 'Logged in'} — saving your experiment...`,
      });

      // Close modal and trigger save
      onClose();
      onSaveSuccess?.();
    } catch (error) {
      toast({
        title: 'Authentication Error',
        description: error instanceof Error ? error.message : 'Authentication failed',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={onClose}
      style={{ backgroundColor: 'rgba(0,0,0,0.4)' }}
    >
      <div
        className="rounded-[16px] p-8 max-w-sm w-full mx-4"
        style={{ backgroundColor: 'var(--surface-bg)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="font-heading mb-2" style={{ fontSize: 24 }}>
          {mode === 'signup' ? 'Save your results' : 'Sign in to save'}
        </h2>
        <p className="font-caption mb-6" style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
          {mode === 'signup'
            ? 'Create a free account to save validation experiments and track results across sessions'
            : 'Sign in to your account to save validation experiments'}
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
                backgroundColor: 'var(--surface-card)',
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
                backgroundColor: 'var(--surface-card)',
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
            {isLoading ? 'Loading...' : mode === 'signup' ? 'Create account & save' : 'Sign in & save'}
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
            {mode === 'signup' ? 'Sign in instead' : 'Create account'}
          </button>
        </div>

        <button
          onClick={onClose}
          style={{
            width: '100%',
            marginTop: 16,
            padding: '10px 16px',
            backgroundColor: 'transparent',
            color: 'var(--text-muted)',
            border: '1px solid var(--divider-light)',
            borderRadius: 8,
            fontSize: 13,
            fontWeight: 500,
            cursor: 'pointer',
            fontFamily: "'Inter', sans-serif",
          }}
        >
          Continue exploring (lose results on refresh)
        </button>
      </div>
    </div>
  );
}
