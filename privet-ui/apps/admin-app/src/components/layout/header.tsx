"use client";

import { motion } from "framer-motion";
import { Button, ThemeToggle } from "@privet-ui/shared";
import { Bell, Search, User, LogOut } from "lucide-react";
import { Breadcrumb } from "@/components/ui/breadcrumb";

export function Header() {
  return (
    <div className="border-b bg-card">
      <div className="h-16 px-6 flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <div className="relative max-w-md flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search users, conversations..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button variant="ghost" size="icon">
              <Bell className="w-5 h-5" />
            </Button>
          </motion.div>
          
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button variant="ghost" size="icon">
              <User className="w-5 h-5" />
            </Button>
          </motion.div>
          
          <ThemeToggle />
          
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button variant="ghost" size="icon">
              <LogOut className="w-5 h-5" />
            </Button>
          </motion.div>
        </div>
      </div>
      
      <div className="px-6 py-3 border-t bg-background/50">
        <Breadcrumb />
      </div>
    </div>
  );
}