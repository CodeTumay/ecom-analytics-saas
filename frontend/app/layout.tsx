import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JewelPilot",
  description: "Accessory Retail Copilot for jewelry, accessories, boutique fashion, and lifestyle retail brands"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
