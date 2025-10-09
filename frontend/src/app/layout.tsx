import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Toaster } from "react-hot-toast";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "IT Analytics Platform - Operational Risk Early Warning System",
  description: "AI-Powered IT Services Project Analytics with Real-time Risk Detection",
  keywords: ["IT Analytics", "Risk Management", "Project Management", "AI", "Machine Learning"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} antialiased`}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              className: 'glass',
              style: {
                background: 'hsl(var(--color-card))',
                color: 'hsl(var(--color-foreground))',
                backdropFilter: 'blur(10px)',
                border: '1px solid hsl(var(--color-border))',
                borderRadius: '12px',
              },
              success: {
                iconTheme: {
                  primary: 'hsl(var(--color-success))',
                  secondary: 'hsl(var(--color-primary-foreground))',
                },
              },
              error: {
                iconTheme: {
                  primary: 'hsl(var(--color-destructive))',
                  secondary: 'hsl(var(--color-primary-foreground))',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}
