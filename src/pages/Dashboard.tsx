import { useEffect, useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { listIdeas, deleteIdea, type IdeaResponse } from '@/api/ideas';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, ArrowRight, LogOut, Search, BarChart3 } from 'lucide-react';
import type { MetricTarget } from '@/types/research-ui';
import { createDefaultValidationMetrics } from '@/lib/research-ui-config';

const MODULE_LABELS = [
  { key: 'has_decompose', label: 'Decompose' },
  { key: 'has_discover', label: 'Discover' },
  { key: 'has_analyze', label: 'Analyze' },
  { key: 'has_setup', label: 'Setup' },
  { key: 'has_validate', label: 'Validate' },
] as const;

type Verdict = 'awaiting' | 'go' | 'pivot' | 'kill';
type DashboardTab = 'ideas' | 'experiments';

const Dashboard = () => {
  const { user, profile, loading: authLoading, signOut } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [ideas, setIdeas] = useState<IdeaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<DashboardTab>('ideas');
  const [metrics, setMetrics] = useState<MetricTarget[]>(createDefaultValidationMetrics());

  useEffect(() => {
    if (!authLoading && !user) navigate('/auth');
  }, [authLoading, user, navigate]);

  useEffect(() => {
    if (user) loadIdeas();
  }, [user]);

  const loadIdeas = async () => {
    try {
      setLoading(true);
      const data = await listIdeas();
      setIdeas(data);
    } catch (err: any) {
      toast({ title: 'Failed to load ideas', description: err.message, variant: 'destructive' });
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

  const handleSignOut = async () => { await signOut(); navigate('/'); };

  const updateMetric = (id: string, val: number) => {
    setMetrics((prev) => prev.map((m) => (m.id === id ? { ...m, actual: val } : m)));
  };

  const { verdict, reasoning } = useMemo(() => {
    const signups = metrics.find((m) => m.id === 'signups')?.actual || 0;
    const switchRate = metrics.find((m) => m.id === 'switch')?.actual || 0;
    const price = metrics.find((m) => m.id === 'price')?.actual || 0;
    const hasData = signups > 0 || switchRate > 0 || price > 0;
    if (!hasData) return { verdict: 'awaiting' as Verdict, reasoning: 'Enter your experiment results to get a recommendation.' };
    if (signups >= 150 && switchRate >= 60 && price >= 8)
      return { verdict: 'go' as Verdict, reasoning: 'Strong demand signal with healthy price tolerance. Move forward.' };
    if (signups < 30 && switchRate < 30)
      return { verdict: 'kill' as Verdict, reasoning: 'Low interest. Consider a different value proposition.' };
    if (signups >= 80 && switchRate >= 40)
      return { verdict: 'pivot' as Verdict, reasoning: 'Moderate interest — refine positioning or pricing.' };
    if (price < 6 && signups > 50)
      return { verdict: 'pivot' as Verdict, reasoning: 'Interest exists but price tolerance is low.' };
    return { verdict: 'pivot' as Verdict, reasoning: 'Mixed signals. Key metrics need improvement.' };
  }, [metrics]);

  const signupsVal = metrics.find((m) => m.id === 'signups')?.actual || 0;
  const switchVal = metrics.find((m) => m.id === 'switch')?.actual || 0;
  const priceVal = metrics.find((m) => m.id === 'price')?.actual || 0;
  const demandStrength = signupsVal >= 100 ? 'High' : signupsVal >= 50 ? 'Medium' : 'Low';
  const priceAcceptance = priceVal >= 10 ? 'Strong' : priceVal >= 7 ? 'Moderate' : 'Weak';
  const conversionEst = signupsVal > 0 ? Math.round((switchVal / 100) * signupsVal) : 0;

  const vc: Record<Verdict, { label: string; color: string; bg: string; border: string }> = {
    awaiting: { label: 'Awaiting data', color: 'var(--text-muted)', bg: 'var(--surface-input)', border: 'var(--divider)' },
    go: { label: 'GO', color: '#1a7a63', bg: 'rgba(45,139,117,0.06)', border: 'rgba(45,139,117,0.15)' },
    pivot: { label: 'PIVOT', color: '#b87a0a', bg: 'rgba(212,136,15,0.06)', border: 'rgba(212,136,15,0.15)' },
    kill: { label: 'NOT VIABLE', color: '#c43c3c', bg: 'rgba(224,82,82,0.06)', border: 'rgba(224,82,82,0.15)' },
  };
  const v = vc[verdict];

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
      <nav className="flex items-center justify-between px-6 border-b" style={{ height: 64, borderColor: 'var(--divider)', backgroundColor: 'var(--surface-bg)' }}>
        <Link to="/" style={{ fontSize: 18, textDecoration: 'none', color: 'inherit' }}>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Launch</span>
          <span style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic' }}>Lens</span>
        </Link>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/research')} className="gap-1.5">
            <Search className="w-3.5 h-3.5" /> New idea
          </Button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium" style={{ backgroundColor: 'var(--accent-purple)', color: '#fff' }}>
              {initials}
            </div>
            <button onClick={handleSignOut} className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}>
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Tab switcher */}
        <div className="flex gap-1 mb-8 rounded-xl p-1" style={{ backgroundColor: 'var(--surface-input)', width: 'fit-content' }}>
          {([
            { id: 'ideas' as DashboardTab, label: 'My Ideas', icon: Search },
            { id: 'experiments' as DashboardTab, label: 'Experiment Dashboard', icon: BarChart3 },
          ]).map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg transition-all duration-200"
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                fontWeight: activeTab === tab.id ? 500 : 400,
                color: activeTab === tab.id ? 'var(--text-primary)' : 'var(--text-muted)',
                backgroundColor: activeTab === tab.id ? 'var(--surface-card)' : 'transparent',
                boxShadow: activeTab === tab.id ? '0 1px 3px rgba(0,0,0,0.06)' : 'none',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              <tab.icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── IDEAS TAB ── */}
        {activeTab === 'ideas' && (
          <>
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-2xl font-medium" style={{ fontFamily: "'Instrument Serif', serif", color: 'var(--text-primary)' }}>
                  Your ideas
                </h1>
                <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
                  {ideas.length} saved idea{ideas.length !== 1 ? 's' : ''}
                </p>
              </div>
              <Button onClick={() => navigate('/research')} className="gap-1.5">
                <Plus className="w-4 h-4" /> Research new idea
              </Button>
            </div>

            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-24 rounded-xl animate-pulse" style={{ backgroundColor: 'var(--surface-input)' }} />
                ))}
              </div>
            ) : ideas.length === 0 ? (
              <div className="text-center py-16 rounded-2xl" style={{ backgroundColor: 'var(--surface-card)', border: '1px solid var(--divider)' }}>
                <p className="text-lg font-medium mb-2" style={{ color: 'var(--text-primary)', fontFamily: "'Instrument Serif', serif" }}>No ideas yet</p>
                <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>Start researching your first startup idea</p>
                <Button onClick={() => navigate('/research')} className="gap-1.5"><Plus className="w-4 h-4" /> Research an idea</Button>
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
                        <h3 className="font-medium text-base truncate" style={{ color: 'var(--text-primary)', fontFamily: "'Instrument Serif', serif" }}>
                          {idea.title}
                        </h3>
                        {idea.description && <p className="text-sm mt-1 truncate" style={{ color: 'var(--text-secondary)' }}>{idea.description}</p>}
                        <div className="flex gap-1.5 mt-3 flex-wrap">
                          {MODULE_LABELS.map(({ key, label }) => (
                            <Badge
                              key={key}
                              variant={idea[key] ? 'default' : 'outline'}
                              className="text-[10px] px-2 py-0.5"
                              style={idea[key] ? { backgroundColor: 'var(--accent-purple)', color: '#fff' } : { borderColor: 'var(--divider-section)', color: 'var(--text-muted)' }}
                            >
                              {label}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{new Date(idea.updated_at).toLocaleDateString()}</span>
                        <button
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-md hover:bg-destructive/10"
                          onClick={(e) => { e.stopPropagation(); handleDelete(idea.id); }}
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
          </>
        )}

        {/* ── EXPERIMENT DASHBOARD TAB ── */}
        {activeTab === 'experiments' && (
          <>
            <div className="mb-8">
              <h1 className="text-2xl font-medium" style={{ fontFamily: "'Instrument Serif', serif", color: 'var(--text-primary)' }}>
                Experiment Dashboard
              </h1>
              <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
                Track your validation metrics and get a go/no-go signal.
              </p>
            </div>

            {/* KPI Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12, marginBottom: 24 }}>
              {metrics.map((m) => {
                const pct = Math.min((m.actual / m.target) * 100, 100);
                const statusColor = pct >= 100 ? '#1a7a63' : pct >= 50 ? '#b87a0a' : pct > 0 ? '#c43c3c' : 'var(--text-muted)';
                return (
                  <div key={m.id} className="rounded-xl p-4" style={{ backgroundColor: 'var(--surface-card)', border: '1px solid var(--divider-light)' }}>
                    <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      {m.label}
                    </p>
                    <div className="flex items-baseline gap-1.5" style={{ marginBottom: 10 }}>
                      <input
                        type="number"
                        value={m.actual || ''}
                        onChange={(e) => updateMetric(m.id, Number(e.target.value) || 0)}
                        placeholder="0"
                        style={{
                          width: 64, padding: '6px 8px', borderRadius: 8,
                          border: '1px solid var(--divider-light)', backgroundColor: 'var(--surface-bg)',
                          fontFamily: "'Inter', sans-serif", fontSize: 20, fontWeight: 500,
                          color: 'var(--text-primary)', outline: 'none', fontVariantNumeric: 'tabular-nums',
                        }}
                        onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--accent-purple)'; }}
                        onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--divider-light)'; }}
                      />
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{m.unit}</span>
                    </div>
                    <div style={{ height: 3, borderRadius: 2, backgroundColor: 'var(--divider-light)', overflow: 'hidden', marginBottom: 4 }}>
                      <div style={{ height: '100%', width: `${pct}%`, backgroundColor: statusColor, borderRadius: 2, transition: 'width 400ms cubic-bezier(0.16,1,0.3,1)' }} />
                    </div>
                    <div className="flex justify-between">
                      <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{Math.round(pct)}%</span>
                      <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>target: {m.targetLabel}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Derived Signals */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 24 }}>
              {[
                { label: 'Demand strength', value: demandStrength, color: demandStrength === 'High' ? '#1a7a63' : demandStrength === 'Medium' ? '#b87a0a' : '#c43c3c' },
                { label: 'Est. conversions', value: conversionEst.toString(), color: 'var(--text-primary)' },
                { label: 'Price acceptance', value: priceAcceptance, color: priceAcceptance === 'Strong' ? '#1a7a63' : priceAcceptance === 'Moderate' ? '#b87a0a' : '#c43c3c' },
              ].map((s) => (
                <div key={s.label} className="rounded-xl p-4 text-center" style={{ backgroundColor: 'var(--surface-input)' }}>
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 10, fontWeight: 300, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>
                    {s.label}
                  </p>
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 18, fontWeight: 500, color: s.color, fontVariantNumeric: 'tabular-nums' }}>
                    {s.value}
                  </p>
                </div>
              ))}
            </div>

            {/* Verdict */}
            <div className="rounded-2xl text-center" style={{ padding: '32px 24px', backgroundColor: v.bg, border: `1px solid ${v.border}` }}>
              <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 10, fontWeight: 300, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
                Verdict
              </p>
              <p style={{ fontFamily: "'Instrument Serif', serif", fontSize: 28, fontWeight: 400, color: v.color, letterSpacing: '-0.02em', lineHeight: 1.2, marginBottom: 12 }}>
                {v.label}
              </p>
              <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.7, maxWidth: 460, margin: '0 auto' }}>
                {reasoning}
              </p>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
