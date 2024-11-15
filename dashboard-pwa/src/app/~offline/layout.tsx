import type { Metadata, Viewport } from "next";

import "../globals.css";

import { InstallButton } from "@/components/app/install-button";
import { InstallPromptProvider } from "@/contexts/install-prompt";

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
  return (
    <html lang="en">
      <body className="container m-auto grid min-h-screen grid-rows-[auto,1fr,auto] bg-background px-4 font-sans antialiased">
        <InstallPromptProvider>
          <header className="text-xl font-bold leading-[4rem] p-12 flex gap-8">
            <h1 className="text-3xl font-bold text-white mb-6">
              Taller 2 Dashboard
            </h1>
            <InstallButton />
          </header>
          <main className="px-12">{children}</main>
          <footer className="text-center leading-[4rem] opacity-70">
            © {new Date().getFullYear()} Taller 2 Dashboard
          </footer>
        </InstallPromptProvider>
      </body>
    </html>
  );
}
