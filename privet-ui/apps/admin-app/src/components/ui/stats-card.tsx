"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@privet-ui/shared";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: "default" | "primary" | "success" | "warning" | "danger" | "info";
  isLoading?: boolean;
}

const colorVariants = {
  default: "text-foreground",
  primary: "text-primary",
  success: "text-success",
  warning: "text-warning",
  danger: "text-destructive",
  info: "text-info",
};

export function StatsCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  color = "default",
  isLoading = false,
}: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            {Icon && <Icon className="w-4 h-4" />}
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <div className="h-8 w-16 bg-muted animate-pulse rounded" />
              {description && <div className="h-3 w-24 bg-muted animate-pulse rounded" />}
            </div>
          ) : (
            <>
              <div className={`text-2xl font-bold ${colorVariants[color]}`}>
                {value}
              </div>
              <div className="flex items-center justify-between">
                {description && (
                  <p className="text-xs text-muted-foreground">{description}</p>
                )}
                {trend && (
                  <div className={`text-xs flex items-center gap-1 ${
                    trend.isPositive ? "text-success" : "text-destructive"
                  }`}>
                    <span>{trend.isPositive ? "+" : ""}{trend.value}%</span>
                  </div>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}