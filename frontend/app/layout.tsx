import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Ensemble AI',
  description: 'Multi-model ensemble AI system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uk">
      <body>{children}</body>
    </html>
  );
}
