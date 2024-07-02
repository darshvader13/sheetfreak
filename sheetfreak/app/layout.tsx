import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "sheetfreak",
  description: "Excel x Google Sheets Agent",
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