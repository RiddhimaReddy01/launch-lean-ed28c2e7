import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { getIdea, type IdeaDetailResponse } from '@/api/ideas';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft } from 'lucide-react';

const IdeaDetail = () => {
  const { ideaId } = useParams();
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [idea, setIdea] = useState<IdeaDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/auth');
    }
  }, [authLoading, user, navigate]);

  useEffect(() => {
    if (user && ideaId) {
      setLoading(true);
      getIdea(ideaId)
        .then(setIdea)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [user, ideaId]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--surface-bg)' }}>
        <div className="animate-pulse text-sm" style={{ color: 'var(--text-muted)' }}>Loading…</div>
      </div>
    );
  }

  if (error || !idea) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--surface-bg)' }}>
        <div className="text-center space-y-4">
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{error || 'Idea not found'}</p>
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to dashboard
          </Button>
        </div>
      </div>
    );
  }

  const sections = [
    { key: 'decomposition', label: 'Decomposition' },
    { key: 'discover', label: 'Discover' },
    { key: 'analyze', label: 'Analyze' },
    { key: 'setup', label: 'Setup' },
    { key: 'validation', label: 'Validation' },
  ] as const;

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--surface-bg)' }}>
      <div className="max-w-3xl mx-auto px-6 py-8">
        <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} className="mb-6 gap-1">
          <ArrowLeft className="w-4 h-4" /> Dashboard
        </Button>

        <h1
          className="text-3xl mb-2"
          style={{ fontFamily: "'Instrument Serif', serif", color: 'var(--text-primary)' }}
        >
          {idea.title}
        </h1>

        {idea.description && (
          <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>{idea.description}</p>
        )}

        <div className="flex gap-2 mb-8">
          <Badge variant="outline" className="text-xs">{idea.status}</Badge>
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
            Updated {new Date(idea.updated_at).toLocaleDateString()}
          </span>
        </div>

        {/* Research sections */}
        <div className="space-y-4">
          {sections.map(({ key, label }) => {
            const data = idea[key];
            const hasData = data !== null && data !== undefined;

            return (
              <div
                key={key}
                className="rounded-xl p-5"
                style={{ backgroundColor: 'var(--surface-card)', border: '1px solid var(--divider)' }}
              >
                <div className="flex items-center justify-between">
                  <h2 className="font-medium" style={{ color: 'var(--text-primary)' }}>{label}</h2>
                  <Badge
                    variant={hasData ? 'default' : 'outline'}
                    className="text-[10px]"
                    style={hasData ? { backgroundColor: 'var(--accent-purple)', color: '#fff' } : {}}
                  >
                    {hasData ? 'Complete' : 'Not started'}
                  </Badge>
                </div>
                {hasData && (
                  <pre
                    className="mt-3 text-xs overflow-auto max-h-48 rounded-lg p-3"
                    style={{ backgroundColor: 'var(--surface-input)', color: 'var(--text-secondary)' }}
                  >
                    {JSON.stringify(data, null, 2)}
                  </pre>
                )}
              </div>
            );
          })}
        </div>

        {idea.notes && (
          <div className="mt-6 rounded-xl p-5" style={{ backgroundColor: 'var(--surface-card)', border: '1px solid var(--divider)' }}>
            <h2 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>Notes</h2>
            <p className="text-sm whitespace-pre-wrap" style={{ color: 'var(--text-secondary)' }}>{idea.notes}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default IdeaDetail;
