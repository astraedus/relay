'use client';

import { useEffect, useState, useCallback } from 'react';
import { getBriefings, generateBriefing } from '../lib/api';
import type { BriefingRow, BriefingReport, GenerateRequest } from '../lib/types';

// ---- Utility ----

function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

// ---- Status dot ----

function StatusDot({ active }: { active: boolean }) {
  return (
    <span
      style={{
        display: 'inline-block',
        width: '7px',
        height: '7px',
        borderRadius: '50%',
        background: active ? '#7c6af7' : '#333',
        flexShrink: 0,
      }}
    />
  );
}

// ---- Skeleton ----

function Skeleton({ width = '100%', height = 12 }: { width?: string; height?: number }) {
  return (
    <div
      style={{
        height,
        width,
        background: '#1e1e1e',
        borderRadius: '4px',
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
  );
}

// ---- Briefing list item ----

function BriefingListItem({
  briefing,
  selected,
  onClick,
}: {
  briefing: BriefingRow;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      style={{
        padding: '12px 14px',
        borderRadius: '8px',
        border: `1px solid ${selected ? '#7c6af7' : '#222'}`,
        background: selected ? '#110f1f' : '#141414',
        cursor: 'pointer',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        transition: 'border-color 0.15s, background 0.15s',
      }}
      onMouseEnter={(e) => {
        if (!selected) (e.currentTarget as HTMLElement).style.borderColor = '#333';
      }}
      onMouseLeave={(e) => {
        if (!selected) (e.currentTarget as HTMLElement).style.borderColor = '#222';
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <StatusDot active={selected} />
        <span style={{ fontWeight: 600, fontSize: '13px', color: '#f5f5f5', flex: 1 }}>
          {briefing.team_name}
        </span>
        <span style={{ fontSize: '11px', color: '#555' }}>{timeAgo(briefing.created_at)}</span>
      </div>
      <p
        style={{
          fontSize: '12px',
          color: '#888',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          lineHeight: '1.4',
        }}
      >
        {briefing.content?.summary || 'No summary available'}
      </p>
    </div>
  );
}

// ---- Briefing detail ----

function BriefingDetail({ briefing }: { briefing: BriefingRow }) {
  const r: BriefingReport = briefing.content;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#f5f5f5' }}>
            {briefing.team_name}
          </h2>
          <span style={{ fontSize: '12px', color: '#555' }}>
            {new Date(briefing.created_at).toLocaleString()}
          </span>
        </div>
        <p style={{ fontSize: '14px', color: '#ccc', lineHeight: '1.6' }}>{r.summary}</p>
      </div>

      {r.momentum && (
        <div
          style={{
            background: '#0f0e1a',
            border: '1px solid #2a2060',
            borderRadius: '8px',
            padding: '12px 14px',
            fontSize: '13px',
            color: '#a89cf7',
            fontStyle: 'italic',
          }}
        >
          {r.momentum}
        </div>
      )}

      {r.key_decisions && r.key_decisions.length > 0 && (
        <Section title="Key Decisions">
          {r.key_decisions.map((d, i) => (
            <ListItem key={i} text={d} color="#7c6af7" bullet="▸" />
          ))}
        </Section>
      )}

      {r.blockers && r.blockers.length > 0 && (
        <Section title="Blockers">
          {r.blockers.map((b, i) => (
            <ListItem key={i} text={b} color="#f87171" bullet="!" />
          ))}
        </Section>
      )}

      {r.action_items && r.action_items.length > 0 && (
        <Section title="Action Items">
          {r.action_items.map((a, i) => (
            <ListItem key={i} text={a} color="#4ade80" bullet="✓" />
          ))}
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3
        style={{
          fontSize: '11px',
          fontWeight: 600,
          color: '#888',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          marginBottom: '8px',
          paddingBottom: '6px',
          borderBottom: '1px solid #1a1a1a',
        }}
      >
        {title}
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {children}
      </div>
    </div>
  );
}

function ListItem({ text, color, bullet }: { text: string; color: string; bullet: string }) {
  return (
    <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
      <span style={{ color, fontSize: '13px', flexShrink: 0, marginTop: '1px' }}>{bullet}</span>
      <span style={{ fontSize: '13px', color: '#ccc', lineHeight: '1.5' }}>{text}</span>
    </div>
  );
}

// ---- Generate modal ----

function GenerateModal({
  onClose,
  onGenerated,
}: {
  onClose: () => void;
  onGenerated: () => void;
}) {
  const [teamName, setTeamName] = useState('Team');
  const [repos, setRepos] = useState('');
  const [channelId, setChannelId] = useState('');
  const [hours, setHours] = useState('24');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const req: GenerateRequest = {
        team_name: teamName || 'Team',
        github_repos: repos
          .split('\n')
          .map((r) => r.trim())
          .filter(Boolean),
        slack_channel_id: channelId.trim(),
        hours: parseInt(hours, 10) || 24,
      };
      await generateBriefing(req);
      onGenerated();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate briefing');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          background: '#141414',
          border: '1px solid #2a2a2a',
          borderRadius: '12px',
          padding: '24px',
          width: '440px',
          maxWidth: '95vw',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f5f5f5' }}>Generate Briefing</h2>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <Field label="Team Name">
            <input
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              placeholder="e.g. Backend Team"
              style={inputStyle}
            />
          </Field>

          <Field label="GitHub Repos (one per line)">
            <textarea
              value={repos}
              onChange={(e) => setRepos(e.target.value)}
              placeholder="owner/repo&#10;owner/another-repo"
              rows={3}
              style={{ ...inputStyle, resize: 'vertical' }}
            />
          </Field>

          <Field label="Slack Channel ID (optional)">
            <input
              value={channelId}
              onChange={(e) => setChannelId(e.target.value)}
              placeholder="e.g. C0123456789"
              style={inputStyle}
            />
          </Field>

          <Field label="Look-back period (hours)">
            <input
              type="number"
              min={1}
              max={168}
              value={hours}
              onChange={(e) => setHours(e.target.value)}
              style={inputStyle}
            />
          </Field>

          {error && (
            <div
              style={{
                background: '#450a0a',
                border: '1px solid #7f1d1d',
                borderRadius: '6px',
                padding: '8px 12px',
                color: '#fca5a5',
                fontSize: '12px',
              }}
            >
              {error}
            </div>
          )}

          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button type="button" onClick={onClose} style={secondaryBtnStyle}>
              Cancel
            </button>
            <button type="submit" disabled={loading} style={primaryBtnStyle(loading)}>
              {loading ? 'Generating...' : 'Generate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <label style={{ fontSize: '12px', color: '#888', fontWeight: 500 }}>{label}</label>
      {children}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  background: '#0a0a0a',
  border: '1px solid #2a2a2a',
  borderRadius: '6px',
  padding: '8px 10px',
  color: '#f5f5f5',
  fontSize: '13px',
  outline: 'none',
  width: '100%',
};

const secondaryBtnStyle: React.CSSProperties = {
  background: 'transparent',
  border: '1px solid #2a2a2a',
  borderRadius: '6px',
  padding: '8px 16px',
  color: '#888',
  fontSize: '13px',
  cursor: 'pointer',
};

const primaryBtnStyle = (disabled: boolean): React.CSSProperties => ({
  background: disabled ? '#3a3060' : '#7c6af7',
  border: 'none',
  borderRadius: '6px',
  padding: '8px 16px',
  color: '#fff',
  fontSize: '13px',
  fontWeight: 600,
  cursor: disabled ? 'not-allowed' : 'pointer',
  opacity: disabled ? 0.7 : 1,
});

// ---- Main page ----

export default function DashboardPage() {
  const [briefings, setBriefings] = useState<BriefingRow[] | null>(null);
  const [selected, setSelected] = useState<BriefingRow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  const fetchBriefings = useCallback(async () => {
    try {
      const data = await getBriefings(30);
      setBriefings(data);
      if (!selected && data.length > 0) {
        setSelected(data[0]);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load briefings');
    }
  }, [selected]);

  useEffect(() => {
    fetchBriefings();
  }, []);

  const handleGenerated = useCallback(() => {
    fetchBriefings();
  }, [fetchBriefings]);

  const isLoading = briefings === null && error === null;

  return (
    <>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        input:focus, textarea:focus {
          border-color: #7c6af7 !important;
          box-shadow: 0 0 0 2px rgba(124, 106, 247, 0.15);
        }
      `}</style>

      {showModal && (
        <GenerateModal
          onClose={() => setShowModal(false)}
          onGenerated={handleGenerated}
        />
      )}

      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        {/* Top bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '14px', fontWeight: 600, color: '#f5f5f5' }}>Briefings</h1>
            {briefings !== null && (
              <span
                style={{
                  fontSize: '11px',
                  color: '#888',
                  background: '#1e1e1e',
                  border: '1px solid #2a2a2a',
                  borderRadius: '10px',
                  padding: '1px 7px',
                }}
              >
                {briefings.length}
              </span>
            )}
          </div>
          <button
            onClick={() => setShowModal(true)}
            style={{
              background: '#7c6af7',
              border: 'none',
              borderRadius: '6px',
              padding: '7px 14px',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            + Generate Now
          </button>
        </div>

        {error && (
          <div
            style={{
              background: '#450a0a',
              border: '1px solid #7f1d1d',
              borderRadius: '6px',
              padding: '10px 14px',
              color: '#fca5a5',
              fontSize: '13px',
            }}
          >
            Could not reach backend: {error}
          </div>
        )}

        {/* Two-column layout */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '300px 1fr',
            gap: '16px',
            alignItems: 'start',
          }}
        >
          {/* Left: briefings list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  style={{
                    padding: '14px',
                    background: '#141414',
                    border: '1px solid #222',
                    borderRadius: '8px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px',
                  }}
                >
                  <Skeleton width="60%" />
                  <Skeleton width="90%" />
                  <Skeleton width="75%" />
                </div>
              ))
            ) : briefings && briefings.length > 0 ? (
              briefings.map((b) => (
                <BriefingListItem
                  key={b.id}
                  briefing={b}
                  selected={selected?.id === b.id}
                  onClick={() => setSelected(b)}
                />
              ))
            ) : (
              <div
                style={{
                  color: '#555',
                  fontSize: '13px',
                  textAlign: 'center',
                  padding: '40px 0',
                  background: '#111',
                  borderRadius: '8px',
                  border: '1px dashed #222',
                }}
              >
                No briefings yet.
                <br />
                <span
                  onClick={() => setShowModal(true)}
                  style={{ color: '#7c6af7', cursor: 'pointer', textDecoration: 'underline' }}
                >
                  Generate your first one.
                </span>
              </div>
            )}
          </div>

          {/* Right: detail view */}
          <div
            style={{
              background: '#141414',
              border: '1px solid #222',
              borderRadius: '8px',
              padding: '20px',
              minHeight: '400px',
            }}
          >
            {selected ? (
              <BriefingDetail briefing={selected} />
            ) : (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '300px',
                  color: '#444',
                  fontSize: '13px',
                }}
              >
                Select a briefing to view details
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
