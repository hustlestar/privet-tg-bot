"use client";

import { motion } from "framer-motion";
import { Flame, Calendar, Award } from "lucide-react";
import { Card } from "@privet-ui/shared";

interface StreakCounterProps {
  days: number;
  isActive?: boolean;
  weeklyGoal?: number;
  weeklyProgress?: number;
}

export function StreakCounter({ 
  days, 
  isActive = true,
  weeklyGoal = 7,
  weeklyProgress = 5
}: StreakCounterProps) {
  const milestones = [7, 30, 100, 365];
  const nextMilestone = milestones.find(m => m > days) || milestones[milestones.length - 1];
  const progressToNextMilestone = (days / nextMilestone) * 100;

  return (
    <Card className="p-4 bg-card border-2 border-warning/20">
      <div className="flex items-center gap-4">
        {/* Animated flame icon */}
        <motion.div
          className="relative"
          animate={isActive ? {
            scale: [1, 1.1, 1],
          } : {}}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <div className="relative">
            <Flame 
              className={`w-10 h-10 ${
                isActive ? 'text-gamification-streak' : 'text-muted-foreground'
              }`}
              fill={isActive ? "currentColor" : "none"}
            />
            {days > 0 && (
              <motion.div
                className="absolute -inset-2 rounded-full bg-gamification-streak/20"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 0.2, 0.5]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            )}
          </div>
        </motion.div>

        {/* Streak info */}
        <div className="flex-1">
          <div className="flex items-baseline gap-2">
            <motion.span 
              className="text-2xl font-bold text-foreground"
              key={days}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
            >
              {days}
            </motion.span>
            <span className="text-sm text-muted-foreground">day streak</span>
          </div>
          
          {/* Weekly progress */}
          <div className="flex items-center gap-2 mt-1">
            <Calendar className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">
              {weeklyProgress}/{weeklyGoal} days this week
            </span>
          </div>

          {/* Progress to next milestone */}
          {days > 0 && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-muted-foreground">Next milestone</span>
                <span className="text-success font-medium">
                  {nextMilestone} days
                </span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-gamification-streak to-gamification-achievement"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressToNextMilestone}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Achievement badges for milestones */}
        {days >= 7 && (
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 200 }}
            className="flex flex-col gap-1"
          >
            {days >= 7 && (
              <Award className="w-5 h-5 text-gamification-achievement" />
            )}
            {days >= 30 && (
              <Award className="w-5 h-5 text-primary" />
            )}
            {days >= 100 && (
              <Award className="w-5 h-5 text-accent" />
            )}
          </motion.div>
        )}
      </div>

      {/* Motivational message */}
      {isActive && days > 0 && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-xs text-success mt-3 font-medium"
        >
          {days === 1 && "Great start! Keep it going! 🚀"}
          {days > 1 && days < 7 && "Building momentum! 💪"}
          {days >= 7 && days < 30 && "One week strong! You're on fire! 🔥"}
          {days >= 30 && days < 100 && "Incredible dedication! 🌟"}
          {days >= 100 && "Legendary learner! 🏆"}
        </motion.p>
      )}
    </Card>
  );
}