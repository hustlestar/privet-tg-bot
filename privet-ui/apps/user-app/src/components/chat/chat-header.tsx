"use client";

import { motion } from "framer-motion";
import { cn } from "@privet-ui/shared";
import { Bot, Wifi, WifiOff, Brain, Sparkles } from "lucide-react";

interface ChatHeaderProps {
  isConnected: boolean;
}

export function ChatHeader({ isConnected }: ChatHeaderProps) {
  return (
    <div className="border-b p-4 bg-gradient-to-r from-primary/5 to-secondary">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <motion.div
            className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground shadow-lg"
            animate={{
              rotate: [0, 5, -5, 5, 0],
            }}
            transition={{
              duration: 6,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut"
            }}
          >
            <Brain className="w-7 h-7" />
          </motion.div>
          <div>
            <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
              Privet Learning Assistant
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              >
                <Sparkles className="w-4 h-4 text-warning" />
              </motion.div>
            </h2>
            <p className="text-sm text-muted-foreground">
              Your AI language learning companion
            </p>
          </div>
        </div>

        <motion.div
          className="flex items-center gap-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div
            className={cn(
              "w-2 h-2 rounded-full",
              isConnected ? "bg-success" : "bg-destructive"
            )}
          >
            <motion.div
              className={cn(
                "w-2 h-2 rounded-full",
                isConnected ? "bg-success" : "bg-destructive"
              )}
              animate={isConnected ? { scale: [1, 1.5, 1] } : {}}
              transition={{
                duration: 2,
                repeat: Infinity,
              }}
            />
          </div>
          {isConnected ? (
            <Wifi className="w-4 h-4 text-success" />
          ) : (
            <WifiOff className="w-4 h-4 text-destructive" />
          )}
        </motion.div>
      </div>
    </div>
  );
}