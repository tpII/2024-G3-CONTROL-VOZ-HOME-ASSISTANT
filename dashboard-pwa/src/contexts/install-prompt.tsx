// InstallPromptContext.tsx

"use client";

import React, { createContext, useState, useEffect } from "react";

interface InstallPromptContextType {
  deferredPrompt: any;
  isInstallable: boolean;
}

export const InstallPromptContext = createContext<InstallPromptContextType>({
  deferredPrompt: null,
  isInstallable: false,
});

type InstallPromptProviderProps = {
  children: React.ReactNode;
};

export const useInstallPrompt = () => {
  const context = React.useContext(InstallPromptContext);

  if (!context) {
    throw new Error(
      "useInstallPrompt must be used within a InstallPromptProvider"
    );
  }

  return context;
};

export const InstallPromptProvider = ({
  children,
}: InstallPromptProviderProps) => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isInstallable, setIsInstallable] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener(
        "beforeinstallprompt",
        handleBeforeInstallPrompt
      );
    };
  }, []);

  return (
    <InstallPromptContext.Provider value={{ deferredPrompt, isInstallable }}>
      {children}
    </InstallPromptContext.Provider>
  );
};
