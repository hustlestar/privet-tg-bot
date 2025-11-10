"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@privet-ui/shared";
import { 
  Users, 
  MessageSquare, 
  Brain, 
  Mic, 
  Settings, 
  BarChart3, 
  Menu,
  X,
  Home,
  Activity
} from "lucide-react";
import { useRouter, usePathname } from "next/navigation";

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Users", href: "/users", icon: Users },
  { name: "Conversations", href: "/conversations", icon: MessageSquare },
  { name: "Memory & RAG", href: "/memory", icon: Brain },
  { name: "Voice", href: "/voice", icon: Mic },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Health", href: "/health", icon: Activity },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: isOpen ? 0 : -280 }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed top-0 left-0 z-50 h-full w-72 bg-background border-r border-border lg:relative lg:translate-x-0 lg:z-auto"
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h2 className="font-semibold">Privet Admin</h2>
                <p className="text-xs text-muted-foreground">Bot Management</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="lg:hidden"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Button
                  key={item.name}
                  variant={isActive ? "default" : "ghost"}
                  className="w-full justify-start gap-3"
                  onClick={() => {
                    router.push(item.href);
                    setIsOpen(false);
                  }}
                >
                  <item.icon className="w-4 h-4" />
                  {item.name}
                </Button>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                <Settings className="w-4 h-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">Admin Panel</p>
                <p className="text-xs text-muted-foreground">v1.0.0</p>
              </div>
            </div>
          </div>
        </div>
      </motion.aside>
    </>
  );
}