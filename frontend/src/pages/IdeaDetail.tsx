import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getIdea, updateIdea, deleteIdea, getValidationExperiments, createValidationExperiment, exportIdea } from '@/api';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { useToast } from '@/hooks/use-toast';
import type { IdeaDetailResponse } from '@/types/api';

type TabType = 'overview' | 'discover' | 'analyze' | 'setup' | 'validate' | 'notes';

export default function IdeaDetail() {
  const { ideaId } = useParams<{ ideaId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [editingNotes, setEditingNotes] = useState(false);
  const [notesText, setNotesText] = useState('');
  const [editingTags, setEditingTags] = useState(false);
  const [tagsInput, setTagsInput] = useState('');

  // Fetch idea
  const ideaQuery = useQuery({
    queryKey: ['idea', ideaId],
    queryFn: () => getIdea(ideaId!),
    staleTime: 1000 * 60 * 5,
    enabled: Boolean(ideaId),
  });

  // Fetch experiments
  const experimentsQuery = useQuery({
    queryKey: ['experiments', ideaId],
    queryFn: () => getValidationExperiments(ideaId!),
    staleTime: 1000 * 60 * 5,
    enabled: Boolean(ideaId),
  });

  // Update idea mutation
  const updateMutation = useMutation({
    mutationFn: (data: any) => updateIdea(ideaId!, data),
    onSuccess: () => {
      toast({ title: 'Saved!', description: 'Your changes have been saved.' });
      ideaQuery.refetch();
      setEditingNotes(false);
      setEditingTags(false);
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    },
  });

  // Create experiment mutation
  const createExpMutation = useMutation({
    mutationFn: (data: any) => createValidationExperiment(data),
    onSuccess: () => {
      toast({ title: 'Experiment logged!', description: 'Check the verdict below.' });
      experimentsQuery.refetch();
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    },
  });

  // Delete idea mutation
  const deleteMutation = useMutation({
    mutationFn: () => deleteIdea(ideaId!),
    onSuccess: () => {
      toast({ title: 'Deleted', description: 'Idea has been removed.' });
      navigate('/dashboard');
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    },
  });

  // Export PDF
  const handleExportPDF = async () => {
    try {
      const blob = await exportIdea(ideaId!);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${idea?.title || 'idea'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast({ title: 'Downloaded!', description: 'PDF export ready.' });
    } catch (error: any) {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this idea?')) {
      deleteMutation.mutate();
    }
  };

  // Extract data
  const idea = ideaQuery.data;
  const experiments = experimentsQuery.data?.experiments || [];

  if (ideaQuery.isLoading) return <LoadingSpinner message="Loading idea..." />;
  if (!idea) return <div style={{ padding: 40, textAlign: 'center' }}>Idea not found</div>;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--surface-bg)' }}>
      {/* Header */}
      <header style={{ padding: '20px 24px', borderBottom: '1px solid var(--divider-light)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', alignItems: 'center', gap: 16 }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontSize: 20,
              padding: 0,
            }}
          >
            ←
          </button>
          <h1
            style={{
              flex: 1,
              fontFamily: "'Instrument Serif', serif",
              fontSize: 24,
              fontWeight: 400,
              color: 'var(--text-primary)',
              margin: 0,
            }}
          >
            {idea.title}
          </h1>
          <button
            onClick={handleExportPDF}
            style={{
              padding: '8px 16px',
              backgroundColor: 'var(--accent-purple)',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 400,
              cursor: 'pointer',
            }}
          >
            Export PDF
          </button>
          <button
            onClick={handleDelete}
            style={{
              padding: '8px 16px',
              backgroundColor: 'rgba(224, 82, 82, 0.1)',
              color: '#E05252',
              border: 'none',
              borderRadius: 6,
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 400,
              cursor: 'pointer',
            }}
          >
            Delete
          </button>
        </div>
      </header>

      {/* Tab navigation */}
      <div
        style={{
          borderBottom: '1px solid var(--divider-light)',
          display: 'flex',
          gap: 32,
          padding: '0 24px',
          maxWidth: '100%',
          overflowX: 'auto',
        }}
      >
        {(['overview', 'discover', 'analyze', 'setup', 'validate', 'notes'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '16px 0',
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontFamily: "'Inter', sans-serif",
              fontSize: 14,
              fontWeight: activeTab === tab ? 400 : 300,
              color: activeTab === tab ? 'var(--text-primary)' : 'var(--text-muted)',
              borderBottom: activeTab === tab ? '2px solid var(--accent-purple)' : 'none',
              textTransform: 'capitalize',
              whiteSpace: 'nowrap',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 24px 160px' }}>
        {activeTab === 'overview' && <TabOverview idea={idea} />}
        {activeTab === 'discover' && <TabDiscover data={idea.discover} />}
        {activeTab === 'analyze' && <TabAnalyze data={idea.analyze} />}
        {activeTab === 'setup' && <TabSetup data={idea.setup} />}
        {activeTab === 'validate' && (
          <TabValidate
            data={idea.validation}
            experiments={experiments}
            ideaId={ideaId!}
            onCreateExperiment={(data) => createExpMutation.mutate(data)}
            isLoading={createExpMutation.isPending}
          />
        )}
        {activeTab === 'notes' && (
          <TabNotes
            idea={idea}
            editing={editingNotes}
            notesText={notesText}
            setEditingNotes={setEditingNotes}
            setNotesText={setNotesText}
            onSave={() => {
              updateMutation.mutate({ notes: notesText });
            }}
            isSaving={updateMutation.isPending}
          />
        )}
      </div>
    </div>
  );
}

// Tab Components

function TabOverview({ idea }: { idea: IdeaDetailResponse }) {
  const decomp = idea.decomposition as any;
  if (!decomp) return <div>No decomposition data</div>;

  return (
    <div>
      <h2 style={{ fontFamily: "'Instrument Serif', serif", fontSize: 22, marginBottom: 24 }}>Business Breakdown</h2>

      <div
        style={{
          padding: 24,
          backgroundColor: 'white',
          borderRadius: 12,
          border: '1px solid var(--divider-light)',
          marginBottom: 32,
        }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
              Business Type
            </p>
            <p style={{ fontSize: 15, color: 'var(--text-primary)' }}>{decomp.business_type || 'N/A'}</p>
          </div>
          <div>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
              Location
            </p>
            <p style={{ fontSize: 15, color: 'var(--text-primary)' }}>
              {decomp.location?.city}, {decomp.location?.state} || 'N/A'
            </p>
          </div>
          <div>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
              Target Customers
            </p>
            <p style={{ fontSize: 15, color: 'var(--text-primary)' }}>
              {Array.isArray(decomp.target_customers) ? decomp.target_customers.join(', ') : 'N/A'}
            </p>
          </div>
          <div>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
              Price Tier
            </p>
            <p style={{ fontSize: 15, color: 'var(--text-primary)' }}>{decomp.price_tier || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Module completion status */}
      <h3 style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, marginBottom: 16, fontWeight: 500 }}>
        Completion Status
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
        {[
          { name: 'Decompose', done: true },
          { name: 'Discover', done: !!idea.discover },
          { name: 'Analyze', done: !!idea.analyze },
          { name: 'Setup', done: !!idea.setup },
          { name: 'Validate', done: !!idea.validation },
        ].map((item) => (
          <div
            key={item.name}
            style={{
              padding: 12,
              backgroundColor: item.done ? 'rgba(45,139,117,0.06)' : 'rgba(0,0,0,0.03)',
              borderRadius: 8,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <span style={{ fontSize: 16 }}>{item.done ? '✓' : '○'}</span>
            <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: item.done ? 500 : 300 }}>
              {item.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TabDiscover({ data }: { data?: any }) {
  if (!data) return <div style={{ color: 'var(--text-muted)' }}>No discovery data available</div>;

  const discover = data as any;
  const topInsights = discover.insights?.slice(0, 5) || [];

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
        <div
          style={{
            padding: 24,
            backgroundColor: 'white',
            borderRadius: 12,
            border: '1px solid var(--divider-light)',
          }}
        >
          <p style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Sources
          </p>
          <p style={{ fontSize: 32, fontWeight: 600, color: 'var(--accent-purple)' }}>
            {discover.sources?.length || 0}
          </p>
        </div>
        <div
          style={{
            padding: 24,
            backgroundColor: 'white',
            borderRadius: 12,
            border: '1px solid var(--divider-light)',
          }}
        >
          <p style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Insights
          </p>
          <p style={{ fontSize: 32, fontWeight: 600, color: 'var(--accent-teal)' }}>
            {discover.insights?.length || 0}
          </p>
        </div>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: 16 }}>Top Insights</h3>
      {topInsights.length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>No insights found</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {topInsights.map((insight: any, idx: number) => (
            <div
              key={idx}
              style={{
                padding: 16,
                backgroundColor: 'white',
                borderRadius: 8,
                border: '1px solid var(--divider-light)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    backgroundColor: 'rgba(45,139,117,0.06)',
                    color: '#2D8B75',
                    padding: '2px 6px',
                    borderRadius: 4,
                  }}
                >
                  {insight.type}
                </span>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Score: {insight.score?.toFixed(2)}</span>
              </div>
              <p style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 500 }}>{insight.title}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TabAnalyze({ data }: { data?: any }) {
  if (!data) return <div style={{ color: 'var(--text-muted)' }}>No analysis data available</div>;

  const analyzeData = data as any;

  return (
    <div>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
        Market analysis from {analyzeData.section || 'multiple sections'} with detailed opportunity assessment.
      </p>
      <div
        style={{
          padding: 24,
          backgroundColor: 'white',
          borderRadius: 12,
          border: '1px solid var(--divider-light)',
        }}
      >
        <p style={{ color: 'var(--text-secondary)', lineHeight: 1.75, whiteSpace: 'pre-wrap' }}>
          {JSON.stringify(analyzeData.data, null, 2)}
        </p>
      </div>
    </div>
  );
}

function TabSetup({ data }: { data?: any }) {
  if (!data) return <div style={{ color: 'var(--text-muted)' }}>No setup data available</div>;

  const setup = data as any;

  return (
    <div>
      {setup.cost_tiers && setup.cost_tiers.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: 16 }}>Cost Tiers</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 12 }}>
            {setup.cost_tiers.map((tier: any, idx: number) => (
              <div
                key={idx}
                style={{
                  padding: 16,
                  backgroundColor: 'white',
                  borderRadius: 8,
                  border: '1px solid var(--divider-light)',
                }}
              >
                <p style={{ fontWeight: 600, marginBottom: 8 }}>{tier.tier}</p>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                  ${tier.total_range?.min || 0} - ${tier.total_range?.max || 0}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {setup.timeline && setup.timeline.length > 0 && (
        <div>
          <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: 16 }}>Timeline</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {setup.timeline.map((phase: any, idx: number) => (
              <div
                key={idx}
                style={{
                  padding: 12,
                  backgroundColor: 'white',
                  borderRadius: 8,
                  border: '1px solid var(--divider-light)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <p style={{ fontSize: 13, fontWeight: 500 }}>{phase.phase}</p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{phase.weeks} weeks</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TabValidate({
  data,
  experiments,
  ideaId,
  onCreateExperiment,
  isLoading,
}: {
  data?: any;
  experiments: any[];
  ideaId: string;
  onCreateExperiment: (data: any) => void;
  isLoading: boolean;
}) {
  const [showNewForm, setShowNewForm] = useState(false);
  const [formData, setFormData] = useState({
    methods: [] as string[],
    waitlist_signups: '',
    survey_completions: '',
    would_switch_rate: '',
    price_tolerance_avg: '',
    community_engagement: '',
    reddit_upvotes: '',
  });

  const handleMethodToggle = (method: string) => {
    setFormData((prev) => ({
      ...prev,
      methods: prev.methods.includes(method) ? prev.methods.filter((m) => m !== method) : [...prev.methods, method],
    }));
  };

  const handleSubmit = () => {
    onCreateExperiment({
      idea_id: ideaId,
      methods: formData.methods,
      metrics: {
        waitlist_signups: parseInt(formData.waitlist_signups) || 0,
        survey_completions: parseInt(formData.survey_completions) || 0,
        would_switch_rate: parseFloat(formData.would_switch_rate) || 0,
        price_tolerance_avg: parseFloat(formData.price_tolerance_avg) || 0,
        community_engagement: parseInt(formData.community_engagement) || 0,
        reddit_upvotes: parseInt(formData.reddit_upvotes) || 0,
      },
    });
    setShowNewForm(false);
    setFormData({
      methods: [],
      waitlist_signups: '',
      survey_completions: '',
      would_switch_rate: '',
      price_tolerance_avg: '',
      community_engagement: '',
      reddit_upvotes: '',
    });
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'go':
        return { bg: 'rgba(45,139,117,0.06)', text: '#2D8B75' };
      case 'pivot':
        return { bg: 'rgba(212,136,15,0.06)', text: '#D4880F' };
      case 'kill':
        return { bg: 'rgba(224,82,82,0.06)', text: '#E05252' };
      default:
        return { bg: 'var(--surface-input)', text: 'var(--text-muted)' };
    }
  };

  return (
    <div>
      {data && (
        <div style={{ marginBottom: 40 }}>
          <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: 16 }}>Validation Toolkit</h3>

          {data.landing_page && (
            <div
              style={{
                padding: 20,
                backgroundColor: 'white',
                borderRadius: 12,
                border: '1px solid var(--divider-light)',
                marginBottom: 16,
              }}
            >
              <p style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                Landing Page Copy
              </p>
              <p style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{data.landing_page.headline}</p>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12 }}>
                {data.landing_page.subheadline}
              </p>
              <ul style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 20 }}>
                {data.landing_page.benefits?.map((b: string, i: number) => (
                  <li key={i}>{b}</li>
                ))}
              </ul>
            </div>
          )}

          {data.communities && data.communities.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                Communities to Target
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 12 }}>
                {data.communities.slice(0, 6).map((c: any, i: number) => (
                  <div
                    key={i}
                    style={{
                      padding: 12,
                      backgroundColor: 'white',
                      borderRadius: 8,
                      border: '1px solid var(--divider-light)',
                    }}
                  >
                    <p style={{ fontWeight: 500, marginBottom: 4 }}>{c.name}</p>
                    <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{c.platform}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.scorecard && (
            <div
              style={{
                padding: 16,
                backgroundColor: 'rgba(108,92,231,0.05)',
                borderRadius: 8,
                border: '1px solid var(--divider-light)',
              }}
            >
              <p style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>
                Validation Targets
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>Waitlist Target</p>
                  <p style={{ fontSize: 16, fontWeight: 600 }}>{data.scorecard.waitlist_target}</p>
                </div>
                <div>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>Switch Rate Target</p>
                  <p style={{ fontSize: 16, fontWeight: 600 }}>{data.scorecard.switch_pct_target}%</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Experiments section */}
      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: 16 }}>Validation Experiments</h3>

      {experiments && experiments.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          {experiments.map((exp: any) => {
            const color = getVerdictColor(exp.verdict);
            return (
              <div
                key={exp.id}
                style={{
                  padding: 16,
                  backgroundColor: 'white',
                  borderRadius: 8,
                  border: '1px solid var(--divider-light)',
                  marginBottom: 12,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{new Date(exp.created_at).toLocaleDateString()}</p>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      backgroundColor: color.bg,
                      color: color.text,
                      padding: '4px 8px',
                      borderRadius: 4,
                    }}
                  >
                    {exp.verdict}
                  </span>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{exp.reasoning}</p>
                <div style={{ marginTop: 12, display: 'flex', gap: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                  <span>Signups: {exp.waitlist_signups}</span>
                  <span>Switch: {exp.would_switch_rate}%</span>
                  <span>Price: ${exp.price_tolerance_avg}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!showNewForm ? (
        <button
          onClick={() => setShowNewForm(true)}
          style={{
            padding: '10px 16px',
            backgroundColor: 'var(--accent-purple)',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            fontFamily: "'Inter', sans-serif",
            fontSize: 13,
            fontWeight: 400,
            cursor: 'pointer',
          }}
        >
          + Log New Experiment
        </button>
      ) : (
        <div
          style={{
            padding: 20,
            backgroundColor: 'white',
            borderRadius: 8,
            border: '1px solid var(--divider-light)',
          }}
        >
          <p style={{ fontSize: 12, fontWeight: 600, marginBottom: 16 }}>Log Validation Experiment</p>

          <div style={{ marginBottom: 16 }}>
            <p style={{ fontSize: 12, fontWeight: 500, marginBottom: 8 }}>Methods Used</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {['landing_page', 'survey', 'community', 'reddit'].map((method) => (
                <label key={method} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={formData.methods.includes(method)}
                    onChange={() => handleMethodToggle(method)}
                  />
                  <span style={{ fontSize: 12, textTransform: 'capitalize' }}>{method.replace('_', ' ')}</span>
                </label>
              ))}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
            <input
              type="number"
              placeholder="Waitlist Signups"
              value={formData.waitlist_signups}
              onChange={(e) => setFormData({ ...formData, waitlist_signups: e.target.value })}
              style={{ padding: 8, borderRadius: 6, border: '1px solid var(--divider-light)', fontSize: 13 }}
            />
            <input
              type="number"
              placeholder="Survey Completions"
              value={formData.survey_completions}
              onChange={(e) => setFormData({ ...formData, survey_completions: e.target.value })}
              style={{ padding: 8, borderRadius: 6, border: '1px solid var(--divider-light)', fontSize: 13 }}
            />
            <input
              type="number"
              placeholder="Would Switch Rate (%)"
              value={formData.would_switch_rate}
              onChange={(e) => setFormData({ ...formData, would_switch_rate: e.target.value })}
              style={{ padding: 8, borderRadius: 6, border: '1px solid var(--divider-light)', fontSize: 13 }}
            />
            <input
              type="number"
              step="0.1"
              placeholder="Price Tolerance ($)"
              value={formData.price_tolerance_avg}
              onChange={(e) => setFormData({ ...formData, price_tolerance_avg: e.target.value })}
              style={{ padding: 8, borderRadius: 6, border: '1px solid var(--divider-light)', fontSize: 13 }}
            />
            <input
              type="number"
              placeholder="Community Engagement"
              value={formData.community_engagement}
              onChange={(e) => setFormData({ ...formData, community_engagement: e.target.value })}
              style={{ padding: 8, borderRadius: 6, border: '1px solid var(--divider-light)', fontSize: 13 }}
            />
            <input
              type="number"
              placeholder="Reddit Upvotes"
              value={formData.reddit_upvotes}
              onChange={(e) => setFormData({ ...formData, reddit_upvotes: e.target.value })}
              style={{ padding: 8, borderRadius: 6, border: '1px solid var(--divider-light)', fontSize: 13 }}
            />
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              style={{
                padding: '10px 16px',
                backgroundColor: 'var(--accent-purple)',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.6 : 1,
              }}
            >
              Save & Get Verdict
            </button>
            <button
              onClick={() => setShowNewForm(false)}
              style={{
                padding: '10px 16px',
                backgroundColor: 'var(--surface-input)',
                color: 'var(--text-primary)',
                border: 'none',
                borderRadius: 6,
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function TabNotes({
  idea,
  editing,
  notesText,
  setEditingNotes,
  setNotesText,
  onSave,
  isSaving,
}: {
  idea: IdeaDetailResponse;
  editing: boolean;
  notesText: string;
  setEditingNotes: (v: boolean) => void;
  setNotesText: (v: string) => void;
  onSave: () => void;
  isSaving: boolean;
}) {
  if (!editing && !idea.notes) {
    return (
      <button
        onClick={() => {
          setEditingNotes(true);
          setNotesText('');
        }}
        style={{
          padding: '12px 16px',
          backgroundColor: 'var(--surface-input)',
          color: 'var(--accent-purple)',
          border: 'none',
          borderRadius: 6,
          fontFamily: "'Inter', sans-serif",
          fontSize: 13,
          cursor: 'pointer',
        }}
      >
        + Add Notes
      </button>
    );
  }

  return (
    <div>
      {!editing ? (
        <div
          style={{
            padding: 20,
            backgroundColor: 'white',
            borderRadius: 8,
            border: '1px solid var(--divider-light)',
            marginBottom: 16,
          }}
        >
          <p style={{ whiteSpace: 'pre-wrap', color: 'var(--text-secondary)' }}>{idea.notes}</p>
          <button
            onClick={() => {
              setEditingNotes(true);
              setNotesText(idea.notes || '');
            }}
            style={{
              marginTop: 16,
              padding: '8px 12px',
              backgroundColor: 'var(--surface-input)',
              color: 'var(--accent-purple)',
              border: 'none',
              borderRadius: 4,
              fontFamily: "'Inter', sans-serif",
              fontSize: 12,
              cursor: 'pointer',
            }}
          >
            Edit
          </button>
        </div>
      ) : (
        <div>
          <textarea
            value={notesText}
            onChange={(e) => setNotesText(e.target.value)}
            style={{
              width: '100%',
              minHeight: 200,
              padding: 12,
              borderRadius: 6,
              border: '1px solid var(--divider-light)',
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              marginBottom: 12,
              fontFamily: "'Inter', sans-serif",
            }}
            placeholder="Add your notes here..."
          />
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={onSave}
              disabled={isSaving}
              style={{
                padding: '10px 16px',
                backgroundColor: 'var(--accent-purple)',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                cursor: isSaving ? 'not-allowed' : 'pointer',
                opacity: isSaving ? 0.6 : 1,
              }}
            >
              Save Notes
            </button>
            <button
              onClick={() => setEditingNotes(false)}
              style={{
                padding: '10px 16px',
                backgroundColor: 'var(--surface-input)',
                color: 'var(--text-primary)',
                border: 'none',
                borderRadius: 6,
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
