import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VYSE — Competitor Content Intelligence",
  description: "Find what works. Know why. Recreate faster.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  );
}
