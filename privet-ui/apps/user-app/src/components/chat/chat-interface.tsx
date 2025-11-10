"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@privet-ui/shared";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { ChatHeader } from "./chat-header";
import { VoiceRecorder } from "./voice-recorder";
import { useChat } from "@/hooks/useChat";
import { TypingIndicator } from "./typing-indicator";

export function ChatInterface() {
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage, isTyping, isConnected } = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <Card className="w-full h-[600px] flex flex-col shadow-2xl overflow-hidden">
      <ChatHeader isConnected={isConnected} />
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <MessageList messages={messages} />
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <TypingIndicator />
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t p-4">
        <AnimatePresence mode="wait">
          {isVoiceMode ? (
            <motion.div
              key="voice"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <VoiceRecorder
                onClose={() => setIsVoiceMode(false)}
                onTranscript={sendMessage}
              />
            </motion.div>
          ) : (
            <motion.div
              key="text"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <MessageInput
                onSend={sendMessage}
                onVoiceClick={() => setIsVoiceMode(true)}
                disabled={!isConnected}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Card>
  );
}