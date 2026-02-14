import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AWS 認定試験対策クイズアプリ',
  description: 'AWS認定資格の勉強用クイズアプリケーション',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
