"use client";

import { useState, KeyboardEvent } from "react";
import { motion } from "framer-motion";
import { Button } from "@privet-ui/shared";
import { Send, Mic, Paperclip } from "lucide-react";

interface MessageInputProps {
  onSend: (message: string) => void;
  onVoiceClick: () => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, onVoiceClick, disabled }: MessageInputProps) {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage("");
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex gap-2">
      <motion.div className="flex-1 relative">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={disabled}
          className="w-full px-4 py-2 pr-10 rounded-full border bg-background focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
        />
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => {}}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-muted-foreground hover:text-foreground"
        >
          <Paperclip className="w-4 h-4" />
        </motion.button>
      </motion.div>

      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
        <Button
          onClick={onVoiceClick}
          variant="outline"
          size="icon"
          className="rounded-full"
          disabled={disabled}
        >
          <Mic className="w-4 h-4" />
        </Button>
      </motion.div>

      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
        <Button
          onClick={handleSend}
          size="icon"
          className="rounded-full bg-warning hover:bg-warning/90 text-warning-foreground"
          disabled={!message.trim() || disabled}
        >
          <Send className="w-4 h-4" />
        </Button>
      </motion.div>
    </div>
  );
}