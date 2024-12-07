"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import Cookies from "js-cookie";
import { config } from "@/config";

interface WebSocketContextProps {
  connected: boolean;
  ledState: "ON" | "OFF";
  sendMessage: (message: "TURN_ON" | "TURN_OFF") => void;
}

const WebSocketContext = createContext<WebSocketContextProps | null>(null);

export function WebSocketProvider({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  const [connected, setConnected] = useState<boolean>(false);
  const [ledState, setLedState] = useState<"ON" | "OFF">("OFF");
  const socketRef = useRef<WebSocket | null>(null);

  const { webSocketUrl } = config;

  const accessToken = Cookies.get("token");
  const client = Cookies.get("client");
  const uid = Cookies.get("uid");

  useEffect(() => {
    if (!accessToken || !client || !uid) {
      console.error("Required cookies are missing!");
      return;
    }
    const url = `${webSocketUrl}/cable?access-token=${accessToken}&client=${client}&uid=${uid}`;
    const webSocket = new WebSocket(url);

    webSocket.onopen = () => {
      setConnected(true);
      webSocket.send("SUBSCRIBE_LED_STATE");
    };

    webSocket.onmessage = (event: MessageEvent) => {
      try {
        const message = event.data;
        setLedState(message);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    webSocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    webSocket.onclose = () => {
      setConnected(false);
      console.log("WebSocket connection closed");
    };

    socketRef.current = webSocket;

    return () => {
      if (
        socketRef.current &&
        socketRef.current.readyState === WebSocket.OPEN
      ) {
        socketRef.current.close();
      }
    };
  }, []);

  const sendMessage = (message: "TURN_ON" | "TURN_OFF") => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    }
  };

  return (
    <WebSocketContext.Provider
      value={{
        connected,
        ledState,
        sendMessage,
      }}
    >
      {children}
    </WebSocketContext.Provider>
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
