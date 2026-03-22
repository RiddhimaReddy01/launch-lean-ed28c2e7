import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { listIdeas, deleteIdea, type IdeaResponse } from '@/api/ideas';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, ArrowRight, LogOut, Search } from 'lucide-react';

const MODULE_LABELS = [
  { key: 'has_decompose', label: 'Decompose' },
  { key: 'has_discover', label: 'Discover' },
  { key: 'has_analyze', label: 'Analyze' },
  { key: 'has_setup', label: 'Setup' },
  { key: 'has_validate', label: 'Validate' },
] as const;

const Dashboard = () => {
  const { user, profile, loading: authLoading, signOut } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [ideas, setIdeas] = useState<IdeaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/auth');
    }
  }, [authLoading, user, navigate]);

  useEffect(() => {
    if (user) {
      loadIdeas();
    }
  }, [user]);

  const loadIdeas = async () => {
    try {
      setLoading(true);
      const data = await listIdeas();
      setIdeas(data);
    } catch (err: any) {
      toast({
        title: 'Failed to load ideas',
        description: err.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    setDeleting(id);
    try {
      await deleteIdea(id);
      setIdeas((prev) => prev.filter((i) => i.id !== id));
      toast({ title: 'Idea deleted' });
    } catch (err: any) {
      toast({ title: 'Delete failed', description: err.message, variant: 'destructive' });
    } finally {
      setDeleting(null);
    }
  };

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--surface-bg)' }}>
        <div className="animate-pulse text-sm" style={{ color: 'var(--text-muted)' }}>Loading…</div>
      </div>
    );
  }

  const displayName = profile?.display_name || user?.email?.split('@')[0] || 'User';
  const initials = displayName.slice(0, 2).toUpperCase();

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--surface-bg)' }}>
      {/* Nav */}
      <nav
        className="flex items-center justify-between px-6 border-b"
        style={{ height: 64, borderColor: 'var(--divider)', backgroundColor: 'var(--surface-bg)' }}
      >
        <Link to="/" style={{ fontSize: 18, textDecoration: 'none', color: 'inherit' }}>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Launch</span>
          <span style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic' }}>Lens</span>
        </Link>

        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/research')} className="gap-1.5">
            <Search className="w-3.5 h-3.5" />
            New idea
          </Button>
          <div className="flex items-center gap-2">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium"
              style={{ backgroundColor: 'var(--accent-purple)', color: '#fff' }}
            >
              {initials}
            </div>
            <button
              onClick={handleSignOut}
              className="flex items-center gap-1 text-xs"
              style={{ color: 'var(--text-muted)' }}
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-6 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1
              className="text-2xl font-medium"
              style={{ fontFamily: "'Instrument Serif', serif", color: 'var(--text-primary)' }}
            >
              Your ideas
            </h1>
            <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
              {ideas.length} saved idea{ideas.length !== 1 ? 's' : ''}
            </p>
          </div>
          <Button onClick={() => navigate('/research')} className="gap-1.5">
            <Plus className="w-4 h-4" />
            Research new idea
          </Button>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 rounded-xl animate-pulse" style={{ backgroundColor: 'var(--surface-input)' }} />
            ))}
          </div>
        ) : ideas.length === 0 ? (
          <div
            className="text-center py-16 rounded-2xl"
            style={{ backgroundColor: 'var(--surface-card)', border: '1px solid var(--divider)' }}
          >
            <p className="text-lg font-medium mb-2" style={{ color: 'var(--text-primary)', fontFamily: "'Instrument Serif', serif" }}>
              No ideas yet
            </p>
            <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
              Start researching your first startup idea
            </p>
            <Button onClick={() => navigate('/research')} className="gap-1.5">
              <Plus className="w-4 h-4" />
              Research an idea
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {ideas.map((idea) => (
              <div
                key={idea.id}
                className="group rounded-xl p-5 transition-shadow duration-200 hover:shadow-md cursor-pointer"
                style={{ backgroundColor: 'var(--surface-card)', border: '1px solid var(--divider)' }}
                onClick={() => navigate(`/ideas/${idea.id}`)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3
                      className="font-medium text-base truncate"
                      style={{ color: 'var(--text-primary)', fontFamily: "'Instrument Serif', serif" }}
                    >
                      {idea.title}
                    </h3>
                    {idea.description && (
                      <p className="text-sm mt-1 truncate" style={{ color: 'var(--text-secondary)' }}>
                        {idea.description}
                      </p>
                    )}

                    {/* Module progress pills */}
                    <div className="flex gap-1.5 mt-3 flex-wrap">
                      {MODULE_LABELS.map(({ key, label }) => (
                        <Badge
                          key={key}
                          variant={idea[key] ? 'default' : 'outline'}
                          className="text-[10px] px-2 py-0.5"
                          style={
                            idea[key]
                              ? { backgroundColor: 'var(--accent-purple)', color: '#fff' }
                              : { borderColor: 'var(--divider-section)', color: 'var(--text-muted)' }
                          }
                        >
                          {label}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                      {new Date(idea.updated_at).toLocaleDateString()}
                    </span>
                    <button
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-md hover:bg-destructive/10"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(idea.id);
                      }}
                      disabled={deleting === idea.id}
                    >
                      <Trash2 className="w-3.5 h-3.5 text-destructive" />
                    </button>
                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-60 transition-opacity" style={{ color: 'var(--text-muted)' }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
