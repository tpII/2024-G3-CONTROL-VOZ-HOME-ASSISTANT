"use client";

import React, { createContext, useContext } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import Cookies from "js-cookie";

interface WebSocketContextProps {
  connected: boolean;
  ledState: boolean;
  sendMessage: (message: Record<string, unknown>) => void;
}

const WebSocketContext = createContext<WebSocketContextProps | null>(null);

export function WebSocketProvider({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  const accessToken = Cookies.get("token");
  const client = Cookies.get("client");
  const uid = Cookies.get("uid");
  const websocketURL = `ws://localhost:8080/cable?access-token=${accessToken}&client=${client}&uid=${uid}`;
  const ws = useWebSocket(websocketURL);

  return (
    <WebSocketContext.Provider value={ws}>{children}</WebSocketContext.Provider>
  );
}

export function useWebSocketContext(): WebSocketContextProps {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error(
      "useWebSocketContext must be used within a WebSocketProvider"
    );
  }
  return context;
}
