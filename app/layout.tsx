// app/layout.tsx (Updated)

import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { Analytics } from '@vercel/analytics/next';
import './globals.css';

// --- Import ThemeProvider and Toaster ---
import { ThemeProvider } from "@/components/ThemeProvider"; //
import { Toaster } from "@/components/ui/toaster";       // or sonner if you used that

// --- Fonts (as you had them) ---
const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  // Update title to be more specific
  title: 'YouTube Video Q&A', // Changed from 'v0 App'
  description: 'Ask questions about any YouTube video using AI.', // Changed
  generator: 'v0.app', // You can keep or remove this
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    // Add suppressHydrationWarning for next-themes
    <html lang="en" suppressHydrationWarning>
      <body className={`font-sans antialiased ${_geist.className}`}> {/* Applied Geist font class */}
        {/* --- Wrap children with ThemeProvider --- */}
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          {/* --- Add Toaster component here --- */}
          <Toaster />
        </ThemeProvider>
        <Analytics />
      </body>
    </html>
  );
}