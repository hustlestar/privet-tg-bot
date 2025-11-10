"use client";

import { motion } from "framer-motion";
import { User } from "lucide-react";

export function RecentUsers() {
  // Dummy data for demonstration
  const users = [
    { id: 1, name: "John Doe", username: "@johndoe", time: "2 min ago" },
    { id: 2, name: "Jane Smith", username: "@janesmith", time: "15 min ago" },
    { id: 3, name: "Bob Johnson", username: "@bobjohn", time: "1 hour ago" },
    { id: 4, name: "Alice Brown", username: "@aliceb", time: "2 hours ago" },
    { id: 5, name: "Charlie Wilson", username: "@charlie", time: "3 hours ago" },
  ];

  return (
    <div className="space-y-4">
      {users.map((user, index) => (
        <motion.div
          key={user.id}
          className="flex items-center gap-4"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: index * 0.05 }}
        >
          <motion.div
            className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center"
            whileHover={{ scale: 1.1 }}
          >
            <User className="w-5 h-5 text-primary" />
          </motion.div>
          <div className="flex-1">
            <p className="text-sm font-medium">{user.name}</p>
            <p className="text-xs text-muted-foreground">{user.username}</p>
          </div>
          <span className="text-xs text-muted-foreground">{user.time}</span>
        </motion.div>
      ))}
    </div>
  );
}