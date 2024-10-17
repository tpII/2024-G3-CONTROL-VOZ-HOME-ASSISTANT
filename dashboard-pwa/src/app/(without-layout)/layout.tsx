import { Metadata, Viewport } from "next";

import "../globals.css";

export const metadata: Metadata = {
  title: "Taller 2 Dashboard",
  description:
    "Dashboard para el control del sistema implementado en Taller de Proyecto 2",
  icons: {
    icon: "/icons/192x192.png",
    apple: "/icons/192x192.png",
  },
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#f472b6",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const year = new Date().getFullYear();
  return (
    <html lang="en">
      <body className="container px-0 m-auto grid min-h-screen grid-rows-[1fr,auto] bg-background font-sans antialiased">
        <main className="px-8 md:px-12">{children}</main>
        <footer className="text-center leading-[4rem] opacity-70">
          © {year} Taller 2 Dashboard
        </footer>
      </body>
    </html>
  );
}
