"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@privet-ui/shared";
import { DollarSign, TrendingUp, BarChart3, Activity, Eye, Calendar } from "lucide-react";
import { useAdminApi } from "@/hooks/useApi";
import { StatsCard } from "@/components/ui/stats-card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { DataTable } from "@/components/ui/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { format } from "date-fns";

interface UsageRecord {
  id: number;
  user_id?: number;
  service_type: string;
  provider: string;
  model: string;
  tokens_used?: number;
  cost: number;
  created_at: string;
}

interface ModelStats {
  model: string;
  provider: string;
  service_type: string;
  total_requests: number;
  total_cost: number;
  total_tokens: number;
}

export default function ExpensesPage() {
  const [timeRange, setTimeRange] = useState(30);
  const { 
    useTotalCosts, 
    useCostBreakdown, 
    useRecentUsage, 
    useModelUsage,
    useUsageStats 
  } = useAdminApi();

  // Fetch data
  const { data: totalCosts, isLoading: totalLoading } = useTotalCosts(undefined, timeRange);
  const { data: breakdown, isLoading: breakdownLoading } = useCostBreakdown(undefined, timeRange);
  const { data: recentUsage, isLoading: recentLoading } = useRecentUsage(undefined, 20);
  const { data: modelUsage, isLoading: modelLoading } = useModelUsage(timeRange);
  const { data: usageStats, isLoading: statsLoading } = useUsageStats(undefined, undefined, undefined, timeRange);

  const isLoading = totalLoading || breakdownLoading || recentLoading || modelLoading || statsLoading;

  // Columns for recent usage table
  const recentUsageColumns: ColumnDef<UsageRecord>[] = [
    {
      accessorKey: "service_type",
      header: "Service",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            row.getValue("service_type") === "llm" ? "bg-blue-500" :
            row.getValue("service_type") === "embedding" ? "bg-green-500" :
            row.getValue("service_type") === "tts" ? "bg-purple-500" :
            row.getValue("service_type") === "stt" ? "bg-orange-500" :
            "bg-gray-500"
          }`} />
          <span className="font-medium capitalize">{row.getValue("service_type")}</span>
        </div>
      ),
    },
    {
      accessorKey: "provider",
      header: "Provider",
      cell: ({ row }) => (
        <span className="text-sm bg-muted px-2 py-1 rounded">
          {row.getValue("provider")}
        </span>
      ),
    },
    {
      accessorKey: "model",
      header: "Model",
      cell: ({ row }) => (
        <span className="text-sm font-mono">
          {row.getValue("model")}
        </span>
      ),
    },
    {
      accessorKey: "tokens_used",
      header: "Tokens",
      cell: ({ row }) => {
        const tokens = row.getValue("tokens_used") as number;
        return tokens ? (
          <span className="text-sm font-mono">{tokens.toLocaleString()}</span>
        ) : "—";
      },
    },
    {
      accessorKey: "cost",
      header: "Cost",
      cell: ({ row }) => {
        const cost = row.getValue("cost") as number;
        return (
          <span className="text-sm font-mono text-success">
            ${cost.toFixed(6)}
          </span>
        );
      },
    },
    {
      accessorKey: "created_at",
      header: "Time",
      cell: ({ row }) => {
        const date = row.getValue("created_at") as string;
        return (
          <span className="text-sm text-muted-foreground">
            {format(new Date(date), "MMM d, HH:mm")}
          </span>
        );
      },
    },
  ];

  // Columns for model usage table
  const modelUsageColumns: ColumnDef<ModelStats>[] = [
    {
      accessorKey: "model",
      header: "Model",
      cell: ({ row }) => (
        <div>
          <div className="font-medium">{row.getValue("model")}</div>
          <div className="text-xs text-muted-foreground">
            {row.original.provider} • {row.original.service_type}
          </div>
        </div>
      ),
    },
    {
      accessorKey: "total_requests",
      header: "Requests",
      cell: ({ row }) => (
        <span className="font-mono">{row.getValue("total_requests")}</span>
      ),
    },
    {
      accessorKey: "total_tokens",
      header: "Tokens",
      cell: ({ row }) => {
        const tokens = row.getValue("total_tokens") as number;
        return tokens ? (
          <span className="font-mono">{tokens.toLocaleString()}</span>
        ) : "—";
      },
    },
    {
      accessorKey: "total_cost",
      header: "Total Cost",
      cell: ({ row }) => {
        const cost = row.getValue("total_cost") as number;
        return (
          <span className="font-mono text-success font-medium">
            ${cost.toFixed(4)}
          </span>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Expense Tracking</h1>
            <p className="text-muted-foreground">
              Monitor AI service usage and costs
            </p>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="px-3 py-2 border border-input bg-background rounded-md text-sm"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        <StatsCard
          title="Total Cost"
          value={`$${totalCosts?.data?.total_cost?.toFixed(4) || "0.0000"}`}
          description={`Last ${timeRange} days`}
          icon={DollarSign}
          color="primary"
          isLoading={isLoading}
        />
        
        <StatsCard
          title="Total Requests"
          value={totalCosts?.data?.total_requests || 0}
          description="API calls made"
          icon={Activity}
          color="info"
          isLoading={isLoading}
        />
        
        <StatsCard
          title="Total Tokens"
          value={totalCosts?.data?.total_tokens?.toLocaleString() || "0"}
          description="Tokens processed"
          icon={BarChart3}
          color="success"
          isLoading={isLoading}
        />
        
        <StatsCard
          title="Avg Cost/Request"
          value={totalCosts?.data?.total_requests > 0 
            ? `$${(totalCosts.data.total_cost / totalCosts.data.total_requests).toFixed(6)}`
            : "$0.000000"
          }
          description="Per API call"
          icon={TrendingUp}
          color="warning"
          isLoading={isLoading}
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid gap-6 lg:grid-cols-2"
      >
        <Card>
          <CardHeader>
            <CardTitle>Model Usage Breakdown</CardTitle>
            <CardDescription>
              Cost and usage by AI model
            </CardDescription>
          </CardHeader>
          <CardContent>
            {modelLoading ? (
              <LoadingSpinner className="h-[300px]" text="Loading model data..." />
            ) : modelUsage?.data?.length ? (
              <DataTable
                columns={modelUsageColumns}
                data={modelUsage.data}
                pageSize={10}
              />
            ) : (
              <EmptyState
                icon={BarChart3}
                title="No Model Usage"
                description="No AI model usage found for this period"
                className="h-[300px]"
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Usage</CardTitle>
            <CardDescription>
              Latest API calls and costs
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recentLoading ? (
              <LoadingSpinner className="h-[300px]" text="Loading recent usage..." />
            ) : recentUsage?.data?.length ? (
              <DataTable
                columns={recentUsageColumns}
                data={recentUsage.data}
                pageSize={10}
              />
            ) : (
              <EmptyState
                icon={Activity}
                title="No Recent Usage"
                description="No recent API usage found"
                className="h-[300px]"
              />
            )}
          </CardContent>
        </Card>
      </motion.div>

      {breakdown?.data && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Cost Breakdown</CardTitle>
              <CardDescription>
                Detailed breakdown by service type and provider
              </CardDescription>
            </CardHeader>
            <CardContent>
              {breakdownLoading ? (
                <LoadingSpinner className="h-[200px]" text="Loading breakdown..." />
              ) : (
                <div className="grid gap-4 md:grid-cols-3">
                  {Object.entries(breakdown.data).map(([key, value]: [string, any]) => (
                    <div key={key} className="p-4 border rounded-lg">
                      <h4 className="font-medium capitalize mb-2">{key.replace('_', ' ')}</h4>
                      <div className="space-y-2">
                        {typeof value === 'object' && value !== null ? (
                          Object.entries(value).map(([subKey, subValue]: [string, any]) => (
                            <div key={subKey} className="flex justify-between items-center text-sm">
                              <span className="text-muted-foreground">{subKey}</span>
                              <span className="font-mono">
                                {typeof subValue === 'number' 
                                  ? subValue < 1 
                                    ? `$${subValue.toFixed(6)}`
                                    : subValue.toLocaleString()
                                  : subValue}
                              </span>
                            </div>
                          ))
                        ) : (
                          <div className="text-sm">
                            <span className="font-mono">
                              {typeof value === 'number' 
                                ? value < 1 
                                  ? `$${value.toFixed(6)}`
                                  : value.toLocaleString()
                                : value}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}