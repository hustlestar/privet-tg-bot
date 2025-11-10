"use client";

import { useState, useEffect, useCallback } from "react";
import { useApi } from "@privet-ui/shared";
import { useMutation } from "@tanstack/react-query";
import { v4 as uuidv4 } from "uuid";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  emotion?: string;
}

export function useChat() {
  const api = useApi();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  // Initialize user on mount
  useEffect(() => {
    const initUser = async () => {
      try {
        const response = await api.users.getUserOrCreateApiV1UsersGetOrCreatePost({
          userCreate: {
            telegram_id: Date.now(), // Using timestamp as unique ID for demo
            username: `user_${Math.random().toString(36).substr(2, 9)}`,
            first_name: "Demo",
            last_name: "User"
          }
        });
        setUserId(response.data.id);
        setIsConnected(true);
      } catch (error) {
        console.error("Failed to initialize user:", error);
        setIsConnected(false);
      }
    };

    initUser();
  }, []);

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!userId) throw new Error("User not initialized");
      
      return api.conversations.processMessageApiV1ConversationsProcessPost({
        conversationRequest: {
          user_id: userId,
          message,
          telegram_id: Date.now(),
          voice_response: false
        }
      });
    },
    onSuccess: (response) => {
      const assistantMessage: Message = {
        id: uuidv4(),
        content: response.data.response,
        role: "assistant",
        timestamp: new Date(),
        emotion: response.data.emotion || undefined
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    },
    onError: (error) => {
      console.error("Failed to send message:", error);
      setIsTyping(false);
      
      // Add error message
      const errorMessage: Message = {
        id: uuidv4(),
        content: "Sorry, I couldn't process your message. Please try again.",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  });

  const sendMessage = useCallback((content: string) => {
    if (!content.trim() || !userId) return;

    // Add user message
    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: "user",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Show typing indicator
    setIsTyping(true);
    
    // Send to API
    sendMessageMutation.mutate(content);
  }, [userId, sendMessageMutation]);

  return {
    messages,
    sendMessage,
    isTyping,
    isConnected,
    isLoading: sendMessageMutation.isPending
  };
}