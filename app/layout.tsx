import type { Metadata } from "next";
import type { ReactNode } from "react";
import "@/index.css";

export const metadata: Metadata = {
  title: "Academic City RAG Assistant",
  description: "RAG chatbot UI for election and budget document analysis.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
