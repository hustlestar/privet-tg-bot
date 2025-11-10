"use client";

import { motion } from "framer-motion";
import { Message } from "./message";

interface MessageListProps {
  messages: Array<{
    id: string;
    content: string;
    role: "user" | "assistant";
    timestamp: Date;
    emotion?: string;
  }>;
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <motion.div
          key={message.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: 0.3,
            delay: index * 0.05,
            ease: "easeOut",
          }}
        >
          <Message {...message} />
        </motion.div>
      ))}
    </div>
  );
}