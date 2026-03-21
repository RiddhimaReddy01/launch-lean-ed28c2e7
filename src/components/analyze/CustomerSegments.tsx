import { MOCK_SEGMENTS } from '@/data/analyze-mock';

export default function CustomerSegments() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {MOCK_SEGMENTS.map((seg) => (
        <div
          key={seg.name}
          className="rounded-[12px] p-6"
          style={{
            backgroundColor: 'var(--surface-card)',
            boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
          }}
        >
          <p
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 15,
              fontWeight: 400,
              color: 'var(--text-primary)',
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
              {Array.from({ length: 10 }).map((_, i) => (
                <div
                  key={i}
                  className="rounded-[2px]"
                  style={{
                    width: 18,
                    height: 6,
                    backgroundColor: i < seg.painIntensity ? 'var(--accent-purple)' : 'var(--divider)',
                    opacity: i < seg.painIntensity ? 0.7 : 0.4,
                    transition: 'background-color 200ms ease-out',
                  }}
                />
              ))}
              <span className="font-caption ml-2" style={{ fontSize: 12 }}>
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
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 13,
                    fontWeight: 300,
                    color: 'var(--text-secondary)',
                    paddingLeft: 12,
                    position: 'relative',
                  }}
                >
                  <span
                    style={{
                      position: 'absolute',
                      left: 0,
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
      ))}
    </div>
  );
}
