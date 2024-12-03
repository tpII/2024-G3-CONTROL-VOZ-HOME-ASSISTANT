import { useEffect, useRef, useState } from "react";
import Cookies from "js-cookie";

interface UseWebSocketProps {
  connected: boolean;
  ledState: "ON" | "OFF";
  sendMessage: (message: "TURN_ON" | "TURN_OFF") => void;
}

export function useWebSocket(): UseWebSocketProps {
  const [connected, setConnected] = useState<boolean>(false);
  const [ledState, setLedState] = useState<"ON" | "OFF">("OFF");
  const socketRef = useRef<WebSocket | null>(null);

  const accessToken = Cookies.get("token");
  const client = Cookies.get("client");
  const uid = Cookies.get("uid");

  useEffect(() => {
    if (!accessToken || !client || !uid) {
      console.error("Required cookies are missing!");
      return;
    }
    const url = `ws://localhost:8080/cable?access-token=${accessToken}&client=${client}&uid=${uid}`;
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

  return { connected, ledState, sendMessage };
}
