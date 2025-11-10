"use client";

import { motion } from "framer-motion";
import { Trophy, Target, Zap } from "lucide-react";

interface ProgressBarProps {
  current: number;
  total: number;
  label?: string;
  level?: "beginner" | "intermediate" | "advanced";
  showMilestones?: boolean;
}

export function ProgressBar({ 
  current, 
  total, 
  label = "Progress",
  level = "beginner",
  showMilestones = true 
}: ProgressBarProps) {
  const percentage = (current / total) * 100;
  const milestones = [25, 50, 75, 100];
  
  const levelColors = {
    beginner: "bg-success",
    intermediate: "bg-primary",
    advanced: "bg-accent"
  };

  const levelBackgrounds = {
    beginner: "bg-level-beginner",
    intermediate: "bg-level-intermediate",
    advanced: "bg-level-advanced"
  };

  return (
    <div className="flex-1 space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-foreground">{label}</span>
        <span className="text-muted-foreground">
          {current}/{total} XP
        </span>
      </div>
      
      <div className="relative">
        {/* Background track */}
        <div className={`h-3 rounded-full ${levelBackgrounds[level]} overflow-hidden`}>
          {/* Progress fill */}
          <motion.div
            className={`h-full ${levelColors[level]} relative`}
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ 
              duration: 1.5,
              ease: "easeOut",
              delay: 0.2 
            }}
          >
            {/* Shimmer effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              animate={{
                x: ["-100%", "200%"]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3
              }}
            />
          </motion.div>
        </div>
        
        {/* Milestone markers */}
        {showMilestones && (
          <div className="absolute inset-0 flex items-center">
            {milestones.map((milestone, index) => {
              const isAchieved = percentage >= milestone;
              return (
                <motion.div
                  key={milestone}
                  className="absolute h-5 w-5 -mt-1"
                  style={{ left: `${milestone}%`, marginLeft: "-10px" }}
                  initial={{ scale: 0 }}
                  animate={{ scale: isAchieved ? 1 : 0.7 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                >
                  <div 
                    className={`
                      h-5 w-5 rounded-full border-2 flex items-center justify-center
                      ${isAchieved 
                        ? 'bg-gamification-achievement border-gamification-achievement' 
                        : 'bg-card border-border'
                      }
                    `}
                  >
                    {milestone === 100 && (
                      <Trophy className="w-3 h-3 text-white" />
                    )}
                    {milestone === 50 && (
                      <Target className="w-3 h-3 text-white" />
                    )}
                    {milestone === 75 && (
                      <Zap className="w-3 h-3 text-white" />
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
      
      {/* Achievement unlocked animation */}
      {percentage >= 100 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-gamification-achievement font-medium flex items-center gap-1"
        >
          <Trophy className="w-4 h-4" />
          Goal achieved! Ready for the next level
        </motion.div>
      )}
    </div>
  );
}