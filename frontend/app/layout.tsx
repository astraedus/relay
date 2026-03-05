import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Relay',
  description: 'Async team briefing agent — daily digests from GitHub and Slack',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header
          style={{
            borderBottom: '1px solid #222',
            padding: '16px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              d="M4 10 L10 4 L16 10"
              stroke="#7c6af7"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M4 14 L10 8 L16 14"
              stroke="#7c6af7"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity="0.5"
            />
          </svg>
          <span
            style={{
              fontWeight: 600,
              fontSize: '15px',
              color: '#f5f5f5',
              letterSpacing: '-0.01em',
            }}
          >
            Relay
          </span>
          <span
            style={{
              fontSize: '12px',
              color: '#888',
              marginLeft: '4px',
            }}
          >
            Daily Team Briefings
          </span>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
