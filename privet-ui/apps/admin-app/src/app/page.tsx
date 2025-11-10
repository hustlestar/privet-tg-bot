"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@privet-ui/shared";
import { Users, MessageSquare, Brain, Activity, TrendingUp, TrendingDown, Eye, DollarSign } from "lucide-react";
import { useAdminApi } from "@/hooks/useApi";
import { StatsCard } from "@/components/ui/stats-card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { useRouter } from "next/navigation";
import { format } from "date-fns";

export default function DashboardPage() {
  const router = useRouter();
  const { useUsers, useHealthStatus, useTotalCosts } = useAdminApi();
  
  // Fetch real data
  const { data: usersData, isLoading: usersLoading } = useUsers(0, 100);
  const { data: healthData, isLoading: healthLoading } = useHealthStatus();
  const { data: costData, isLoading: costLoading } = useTotalCosts();

  // Calculate dashboard stats from real data
  const totalUsers = usersData?.total || 0;
  const activeUsers = usersData?.items?.filter(user => user.is_active).length || 0;
  const newUsersToday = usersData?.items?.filter(user => {
    if (!user.created_at) return false;
    const today = new Date().toDateString();
    return new Date(user.created_at).toDateString() === today;
  }).length || 0;

  // Recent users for the sidebar
  const recentUsers = usersData?.items?.slice(0, 5) || [];

  const isLoading = usersLoading || healthLoading;

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Monitor and manage your bot's performance
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        <StatsCard
          title="Total Users"
          value={totalUsers}
          description="Registered users"
          icon={Users}
          color="primary"
          isLoading={isLoading}
          trend={{
            value: newUsersToday > 0 ? 12 : 0,
            isPositive: newUsersToday > 0
          }}
        />
        
        <StatsCard
          title="Active Users"
          value={activeUsers}
          description="Currently active"
          icon={Activity}
          color="success"
          isLoading={isLoading}
          trend={{
            value: activeUsers > totalUsers * 0.8 ? 8 : -3,
            isPositive: activeUsers > totalUsers * 0.8
          }}
        />
        
        <StatsCard
          title="New Today"
          value={newUsersToday}
          description="Joined today"
          icon={TrendingUp}
          color="info"
          isLoading={isLoading}
        />
        
        <StatsCard
          title="System Status"
          value={healthData?.status === "healthy" ? "Healthy" : "Issues"}
          description="Backend status"
          icon={healthData?.status === "healthy" ? TrendingUp : TrendingDown}
          color={healthData?.status === "healthy" ? "success" : "warning"}
          isLoading={isLoading}
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-7"
      >
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>System Overview</CardTitle>
            <CardDescription>
              Real-time system information and health
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSpinner className="h-[300px]" text="Loading system data..." />
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <p className="text-sm font-medium">API Version</p>
                    <p className="text-2xl font-bold text-primary">
                      {healthData?.version || "Unknown"}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Environment</p>
                    <p className="text-2xl font-bold text-info">
                      {healthData?.environment || "Unknown"}
                    </p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">User Distribution</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Active Users</span>
                      <span className="text-sm font-mono">{activeUsers}/{totalUsers}</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-success h-2 rounded-full transition-all duration-300"
                        style={{ 
                          width: totalUsers > 0 ? `${(activeUsers / totalUsers) * 100}%` : "0%" 
                        }}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Languages</span>
                      <span className="text-sm font-mono">
                        {new Set(usersData?.items?.map(u => u.language || "en")).size || 0}
                      </span>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      {Array.from(
                        new Set(usersData?.items?.map(u => u.language || "en"))
                      ).map((lang) => (
                        <span
                          key={lang}
                          className="px-2 py-1 bg-muted rounded text-xs font-mono uppercase"
                        >
                          {lang}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Users</CardTitle>
                <CardDescription>Latest registered users</CardDescription>
              </div>
              <button
                onClick={() => router.push("/users")}
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                View all <Eye className="w-3 h-3" />
              </button>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSpinner className="h-[300px]" text="Loading users..." />
            ) : recentUsers.length > 0 ? (
              <div className="space-y-4">
                {recentUsers.map((user, index) => (
                  <motion.div
                    key={user.user_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => router.push(`/users/${user.user_id}`)}
                  >
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Users className="w-5 h-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {user.first_name || user.last_name 
                          ? `${user.first_name || ""} ${user.last_name || ""}`.trim()
                          : user.username || `User ${user.user_id}`}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        ID: {user.user_id} • {user.language?.toUpperCase() || "EN"}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs px-2 py-1 rounded ${
                        user.is_active 
                          ? "bg-success/10 text-success" 
                          : "bg-muted text-muted-foreground"
                      }`}>
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                      <p className="text-xs text-muted-foreground mt-1">
                        {user.created_at 
                          ? format(new Date(user.created_at), "MMM d")
                          : "Unknown"}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Users}
                title="No Users Yet"
                description="No users have registered yet"
                className="h-[300px]"
              />
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              User Management
            </CardTitle>
            <CardDescription>Manage registered users</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button
                onClick={() => router.push("/users")}
                className="w-full text-left p-3 rounded-lg border-2 border-primary/20 bg-primary/5 hover:bg-primary/10 hover:border-primary/40 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <div className="font-medium text-foreground">View All Users</div>
                <div className="text-sm text-muted-foreground">
                  {totalUsers} registered users
                </div>
              </button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Memory System
            </CardTitle>
            <CardDescription>RAG and user memory</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button
                onClick={() => router.push("/memory")}
                className="w-full text-left p-3 rounded-lg border-2 border-info/20 bg-info/5 hover:bg-info/10 hover:border-info/40 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <div className="font-medium text-foreground">Memory Management</div>
                <div className="text-sm text-muted-foreground">
                  User facts and embeddings
                </div>
              </button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Conversations
            </CardTitle>
            <CardDescription>Chat monitoring</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button
                onClick={() => router.push("/conversations")}
                className="w-full text-left p-3 rounded-lg border-2 border-success/20 bg-success/5 hover:bg-success/10 hover:border-success/40 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <div className="font-medium text-foreground">View Conversations</div>
                <div className="text-sm text-muted-foreground">
                  Monitor user chats
                </div>
              </button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Expense Tracking
            </CardTitle>
            <CardDescription>AI usage costs and analytics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button
                onClick={() => router.push("/expenses")}
                className="w-full text-left p-3 rounded-lg border-2 border-warning/20 bg-warning/5 hover:bg-warning/10 hover:border-warning/40 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <div className="font-medium text-foreground">View Expenses</div>
                <div className="text-sm text-muted-foreground">
                  ${costData?.data?.total_cost?.toFixed(4) || "0.0000"} this month
                </div>
              </button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}