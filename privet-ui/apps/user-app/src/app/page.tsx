"use client";

import { ChatInterface } from "@/components/chat/chat-interface";
import { StreakCounter } from "@/components/gamification/streak-counter";
import { ProgressBar } from "@/components/gamification/progress-bar";
import { ThemeToggle } from "@privet-ui/shared";
import { motion } from "framer-motion";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-4 bg-background">
      {/* Top bar with progress and streak */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-4xl mb-4"
      >
        <div className="flex items-center justify-between mb-4">
          <ProgressBar 
            current={45} 
            total={100} 
            label="Today's Progress" 
            level="intermediate"
          />
          <div className="flex items-center gap-4">
            <StreakCounter days={7} />
            <ThemeToggle />
          </div>
        </div>
      </motion.div>

      {/* Main chat interface */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="w-full max-w-4xl"
      >
        <ChatInterface />
      </motion.div>
    </main>
  );
}