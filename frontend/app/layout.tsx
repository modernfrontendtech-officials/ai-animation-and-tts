import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Video Factory",
  description: "Self-hosted AI video generation control plane"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
