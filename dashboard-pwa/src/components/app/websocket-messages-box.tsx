"use client";

import { useState, useEffect } from "react";
import Cookies from "js-cookie";

export default function WebSocketMessagesBox() {
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    const accessToken = Cookies.get("token");
    const client = Cookies.get("client");
    const uid = Cookies.get("uid");

    if (!accessToken || !client || !uid) {
      console.error("Required cookies are missing!");
      return;
    }

    const wsUrl = `ws://localhost:8080/cable?access-token=${accessToken}&client=${client}&uid=${uid}`;

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          command: "subscribe",
          identifier: JSON.stringify({
            channel: "ChatChannel",
            room: "my_room",
          }),
        })
      );
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data && data.message) {
        setMessages((prevMessages) => [...prevMessages, data.message]);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div
      className="w-52 h-52 p-2 bg-gray-900 text-white overflow-y-auto"
      style={{ width: "200px", height: "200px" }}
    >
      <h4 className="text-lg font-bold mb-2">Messages</h4>
      <div className="space-y-1 text-sm">
        {messages.length > 0 ? (
          messages.map((message, index) => <p key={index}>{message}</p>)
        ) : (
          <p>No messages yet...</p>
        )}
      </div>
    </div>
  );
}
