import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import { AppProviders } from "@/providers/app-providers";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "SupportAI - AI Customer Support Platform",
  description: "Create AI-powered customer support chatbots trained on your company knowledge base.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${plusJakarta.variable} font-sans`}>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
