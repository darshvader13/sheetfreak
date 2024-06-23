import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "freakinthesheets",
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
