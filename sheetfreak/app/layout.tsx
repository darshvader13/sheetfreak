import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "sheetfreak",
  description: "CalHacks x Skydeck AI Hackathon",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
