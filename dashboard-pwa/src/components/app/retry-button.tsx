"use client";

import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export const RetryButton = () => {
  const [isOnline, setIsOnline] = useState(
    typeof window !== "undefined" ? window.navigator.onLine : true
  );

  const router = useRouter();

  const checkConnection = () => {
    return navigator.onLine;
  };

  const handleRetry = () => {
    console.log("Retrying connection...");
    if (checkConnection()) {
      setIsOnline(true);
    } else {
      setIsOnline(false);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (checkConnection()) {
        setIsOnline(true);
        clearInterval(interval);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isOnline) {
      router.push("/");
    }
  }, [isOnline]);

  return (
    <Button
      onClick={handleRetry}
      className="bg-pink-500 hover:bg-pink-600 text-white"
    >
      Retry Connection
    </Button>
  );
};
