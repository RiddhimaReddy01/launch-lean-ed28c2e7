import { useState } from 'react';
import { MOCK_SEGMENTS } from '@/data/analyze-mock';

export default function CustomerSegments() {
  const [hoveredSegment, setHoveredSegment] = useState<string | null>(null);
  const [hoveredBar, setHoveredBar] = useState<{ segment: string; index: number } | null>(null);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {MOCK_SEGMENTS.map((seg) => {
        const isHovered = hoveredSegment === seg.name;
        return (
          <div
            key={seg.name}
            className="rounded-[12px] p-6 transition-all duration-200"
            style={{
              backgroundColor: 'var(--surface-card)',
              boxShadow: isHovered ? '0 4px 16px rgba(0,0,0,0.07)' : '0 1px 3px rgba(0,0,0,0.04)',
              transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
            }}
            onMouseEnter={() => setHoveredSegment(seg.name)}
            onMouseLeave={() => setHoveredSegment(null)}
          >
            <p
              className="transition-colors duration-200"
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 15,
                fontWeight: 400,
                color: isHovered ? 'var(--accent-purple)' : 'var(--text-primary)',
                marginBottom: 6,
              }}
            >
              {seg.name}
            </p>
            <p className="font-caption" style={{ fontSize: 12, marginBottom: 16 }}>
              {seg.estimatedSize}
            </p>
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 14,
                fontWeight: 300,
                lineHeight: 1.65,
                color: 'var(--text-secondary)',
                marginBottom: 20,
              }}
            >
              {seg.description}
            </p>

            {/* Pain intensity */}
            <div className="mb-4">
              <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 6 }}>
                PAIN INTENSITY
              </p>
              <div className="flex items-center gap-1">
                {Array.from({ length: 10 }).map((_, i) => {
                  const isFilled = i < seg.painIntensity;
                  const isBarHovered = hoveredBar?.segment === seg.name && hoveredBar?.index === i;
                  return (
                    <div
                      key={i}
                      className="rounded-[2px] transition-all duration-150 cursor-pointer"
                      style={{
                        width: 18,
                        height: isBarHovered ? 10 : 6,
                        backgroundColor: isFilled ? 'var(--accent-purple)' : 'var(--divider)',
                        opacity: isFilled ? (isBarHovered ? 1 : 0.7) : 0.4,
                        transform: isBarHovered ? 'translateY(-2px)' : 'translateY(0)',
                      }}
                      onMouseEnter={() => setHoveredBar({ segment: seg.name, index: i })}
                      onMouseLeave={() => setHoveredBar(null)}
                      title={`${i + 1}/10`}
                    />
                  );
                })}
                <span className="font-caption ml-2 transition-colors duration-200" style={{ fontSize: 12, color: hoveredBar?.segment === seg.name ? 'var(--accent-purple)' : undefined }}>
                  {seg.painIntensity}/10
                </span>
              </div>
            </div>

            {/* Cares about */}
            <div>
              <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 8 }}>
                CARES MOST ABOUT
              </p>
              <ul className="flex flex-col gap-1.5">
                {seg.caresMostAbout.map((item) => (
                  <li
                    key={item}
                    className="transition-all duration-150 rounded-[4px] px-1 -mx-1"
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: 13,
                      fontWeight: 300,
                      color: 'var(--text-secondary)',
                      paddingLeft: 16,
                      position: 'relative',
                      cursor: 'default',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(108,92,231,0.04)';
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--text-secondary)';
                    }}
                  >
                    <span
                      style={{
                        position: 'absolute',
                        left: 4,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        width: 4,
                        height: 4,
                        borderRadius: '50%',
                        backgroundColor: 'var(--divider-section)',
                      }}
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        );
      })}
    </div>
  );
}
