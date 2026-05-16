import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ensemble AI",
  description: "Stage 3 MVP",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uk">
      <body className="bg-gray-950 text-gray-100 antialiased">
        {children}
      </body>
    </html>
  );
}