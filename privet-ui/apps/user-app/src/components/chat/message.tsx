"use client";

import { motion } from "framer-motion";
import { cn } from "@privet-ui/shared";
import { User, Bot, Heart, Smile, Frown, Zap, Sparkles } from "lucide-react";

interface MessageProps {
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  emotion?: string;
}

const emotionIcons: Record<string, React.ReactNode> = {
  happy: <Smile className="w-4 h-4 text-yellow-500" />,
  sad: <Frown className="w-4 h-4 text-blue-500" />,
  love: <Heart className="w-4 h-4 text-red-500" />,
  excited: <Zap className="w-4 h-4 text-orange-500" />,
  neutral: <Sparkles className="w-4 h-4 text-gray-500" />,
};

export function Message({ content, role, timestamp, emotion }: MessageProps) {
  const isUser = role === "user";

  return (
    <motion.div
      className={cn(
        "flex gap-3",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
      initial={{ opacity: 0, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className={cn(
          "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center",
          isUser ? "bg-primary text-primary-foreground" : "bg-secondary"
        )}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </motion.div>

      <motion.div
        className={cn(
          "flex flex-col gap-1 max-w-[70%]",
          isUser ? "items-end" : "items-start"
        )}
        layout
      >
        <motion.div
          className={cn(
            "rounded-2xl px-4 py-2",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-secondary text-secondary-foreground"
          )}
          whileHover={{ scale: 1.02 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        >
          <p className="text-sm whitespace-pre-wrap">{content}</p>
        </motion.div>

        <div className="flex items-center gap-2 px-2">
          <span className="text-xs text-muted-foreground">
            {timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
          {emotion && !isUser && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="flex items-center gap-1"
            >
              {emotionIcons[emotion] || emotionIcons.neutral}
            </motion.span>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}