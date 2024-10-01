"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useInstallPrompt } from "@/contexts/install-prompt";

export const InstallButton = () => {
  const { deferredPrompt, isInstallable } = useInstallPrompt();

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
  };

  if (!isInstallable) return null;

  return (
    <Button
      onClick={handleInstallClick}
      className="bg-pink-600 hover:bg-pink-700 text-white"
    >
      <Download className="mr-2 h-4 w-4" />
      Install
    </Button>
  );
};
