import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MoodTune AI - Emotion-Aware Music Recommendations",
  description:
    "Discover music that matches your mood. AI-powered emotion detection with personalized music recommendations.",
  keywords: [
    "music recommendation",
    "emotion detection",
    "AI",
    "mood",
    "Spotify",
    "NLP",
    "BERT",
  ],
  authors: [{ name: "Parth" }],
  openGraph: {
    title: "MoodTune AI - Emotion-Aware Music Recommendations",
    description:
      "Discover music that matches your mood with AI-powered emotion analysis.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>
        <div className="min-h-screen gradient-bg">{children}</div>
      </body>
    </html>
  );
}
