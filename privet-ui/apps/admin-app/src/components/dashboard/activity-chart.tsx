"use client";

import { motion } from "framer-motion";

export function ActivityChart() {
  // Dummy data for demonstration
  const data = [
    { day: "Mon", messages: 120, users: 45 },
    { day: "Tue", messages: 150, users: 52 },
    { day: "Wed", messages: 180, users: 61 },
    { day: "Thu", messages: 165, users: 58 },
    { day: "Fri", messages: 210, users: 70 },
    { day: "Sat", messages: 185, users: 65 },
    { day: "Sun", messages: 160, users: 55 },
  ];

  const maxMessages = Math.max(...data.map(d => d.messages));

  return (
    <div className="h-[300px] flex items-end justify-between gap-4">
      {data.map((item, index) => (
        <div key={item.day} className="flex-1 flex flex-col items-center gap-2">
          <div className="w-full flex gap-1 items-end h-[250px]">
            <motion.div
              className="flex-1 bg-chart-1 rounded-t shadow-sm"
              initial={{ height: 0 }}
              animate={{ height: `${(item.messages / maxMessages) * 100}%` }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            />
            <motion.div
              className="flex-1 bg-chart-2 rounded-t shadow-sm"
              initial={{ height: 0 }}
              animate={{ height: `${(item.users / maxMessages) * 100}%` }}
              transition={{ duration: 0.5, delay: index * 0.1 + 0.05 }}
            />
          </div>
          <span className="text-xs text-muted-foreground">{item.day}</span>
        </div>
      ))}
    </div>
  );
}