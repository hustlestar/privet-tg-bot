"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@privet-ui/shared";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string;
  change: string;
  icon: React.ReactNode;
}

export function StatsCard({ title, value, change, icon }: StatsCardProps) {
  const isPositive = change.startsWith("+");
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <motion.div
          whileHover={{ scale: 1.1 }}
          className="text-muted-foreground"
        >
          {icon}
        </motion.div>
      </CardHeader>
      <CardContent>
        <motion.div
          className="text-2xl font-bold"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200 }}
        >
          {value}
        </motion.div>
        <div className="flex items-center gap-1 text-xs">
          {isPositive ? (
            <TrendingUp className="w-3 h-3 text-success" />
          ) : (
            <TrendingDown className="w-3 h-3 text-destructive" />
          )}
          <span className={isPositive ? "text-success" : "text-destructive"}>
            {change}
          </span>
          <span className="text-muted-foreground">from last month</span>
        </div>
      </CardContent>
    </Card>
  );
}