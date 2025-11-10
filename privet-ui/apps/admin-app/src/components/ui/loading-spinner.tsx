"use client";

import { motion } from "framer-motion";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  className?: string;
}

const sizeVariants = {
  sm: "h-4 w-4",
  md: "h-8 w-8", 
  lg: "h-12 w-12",
};

export function LoadingSpinner({ 
  size = "md", 
  text,
  className = ""
}: LoadingSpinnerProps) {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className="flex flex-col items-center gap-3">
        <motion.div
          className={`${sizeVariants[size]} border-2 border-primary/20 border-t-primary rounded-full`}
          animate={{ rotate: 360 }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        {text && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-sm text-muted-foreground"
          >
            {text}
          </motion.p>
        )}
      </div>
    </div>
  );
}