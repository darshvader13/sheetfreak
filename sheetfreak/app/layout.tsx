import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "sheetfreak",
  description: "Google Sheets x Excel Agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <link rel="icon" type="image/png" sizes="any" href="/big logo.png"/>
      <body>{children}</body>
    </html>
  );
}