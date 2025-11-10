"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button } from "@privet-ui/shared";
import { ArrowLeft, Edit, Trash2, MessageSquare, Brain, Activity, Calendar, Mic, Play, Eye } from "lucide-react";
import { useAdminApi } from "@/hooks/useApi";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { DataTable } from "@/components/ui/data-table";
import { ColumnDef } from "@tanstack/react-table";
import type { UserFact } from "@privet/api-client";

interface UserDetailPageProps {
  params: { id: string };
}

export default function UserDetailPage({ params }: UserDetailPageProps) {
  const router = useRouter();
  const userId = parseInt(params.id);
  
  const { 
    useUser, 
    useUserStats, 
    useConversationHistory, 
    useUserFacts,
    useDeleteUser 
  } = useAdminApi();

  const { data: user, isLoading: userLoading } = useUser(userId);
  const { data: stats, isLoading: statsLoading } = useUserStats(userId);
  const { data: conversations, isLoading: conversationsLoading, error: conversationsError } = useConversationHistory(userId, 10);
  const { data: facts, isLoading: factsLoading } = useUserFacts(userId, 10);
  const deleteUser = useDeleteUser();

  const factColumns: ColumnDef<UserFact>[] = [
    {
      accessorKey: "fact_text",
      header: "Fact",
      cell: ({ row }) => (
        <div className="max-w-md">
          {row.getValue("fact_text")}
        </div>
      ),
    },
    {
      accessorKey: "category",
      header: "Category",
      cell: ({ row }) => (
        <div className="text-xs bg-muted px-2 py-1 rounded">
          {row.getValue("category") || "General"}
        </div>
      ),
    },
    {
      accessorKey: "created_at",
      header: "Created",
      cell: ({ row }) => {
        const date = row.getValue("created_at") as string;
        return (
          <div className="text-sm text-muted-foreground">
            {date ? format(new Date(date), "MMM d") : "—"}
          </div>
        );
      },
    },
  ];

  const handleDeleteUser = () => {
    if (confirm("Are you sure you want to delete this user? This action cannot be undone.")) {
      deleteUser.mutate(userId, {
        onSuccess: () => {
          router.push("/users");
        },
      });
    }
  };

  if (userLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <h2 className="text-xl font-semibold">User not found</h2>
        <Button onClick={() => router.push("/users")} className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Users
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => router.push("/users")}>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold">
                {user.first_name || user.last_name 
                  ? `${user.first_name || ""} ${user.last_name || ""}`.trim()
                  : user.username || `User ${user.user_id}`}
              </h1>
              <p className="text-muted-foreground">ID: {user.user_id}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button variant="destructive" onClick={handleDeleteUser}>
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Messages
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_messages || 0}
            </div>
            <p className="text-xs text-muted-foreground">Total sent</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Memory Facts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-info">
              {stats?.facts_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">Stored facts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Active Days
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-success">
              {stats?.active_days || 0}
            </div>
            <p className="text-xs text-muted-foreground">Days used</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Joined
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm font-bold">
              {user.created_at ? format(new Date(user.created_at), "MMM d, yyyy") : "Unknown"}
            </div>
            <p className="text-xs text-muted-foreground">Registration date</p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid gap-6 lg:grid-cols-2"
      >
        <Card>
          <CardHeader>
            <CardTitle>User Information</CardTitle>
            <CardDescription>Basic user profile details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Username</label>
                <p className="text-sm">{user.username || "—"}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Language</label>
                <p className="text-sm uppercase">{user.language || "EN"}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">First Name</label>
                <p className="text-sm">{user.first_name || "—"}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Last Name</label>
                <p className="text-sm">{user.last_name || "—"}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Status</label>
                <p className={`text-sm font-medium ${
                  user.is_active ? "text-success" : "text-muted-foreground"
                }`}>
                  {user.is_active ? "Active" : "Inactive"}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Last Updated</label>
                <p className="text-sm">
                  {user.updated_at ? format(new Date(user.updated_at), "MMM d, yyyy") : "—"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Chat History
            </CardTitle>
            <CardDescription>Latest messages (showing last 5)</CardDescription>
          </CardHeader>
          <CardContent>
            {conversationsLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              </div>
            ) : conversationsError ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-2">Unable to load chat history</p>
                <p className="text-xs text-muted-foreground">There may be a connection issue with the API</p>
              </div>
            ) : conversations?.messages?.length ? (
              <div className="space-y-3">
                <div className="space-y-1 h-72 overflow-y-auto">
                  {conversations.messages.slice(0, 5).map((message, index) => (
                    <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[70%] rounded-lg p-2 relative ${
                        message.role === 'user' 
                          ? 'bg-primary text-primary-foreground' 
                          : 'bg-muted text-foreground border'
                      }`}>
                        <div className="flex items-start gap-2">
                          <p className="text-sm leading-snug flex-1">
                            {message.is_voice ? 
                              (message.transcribed_text || "Voice message") :
                              (message.message_text || "No content")
                            }
                          </p>
                          {message.is_voice && (
                            <button 
                              className={`flex-shrink-0 p-1 rounded-full transition-colors ${
                                message.metadata?.audio_url 
                                  ? 'hover:bg-black/10 cursor-pointer' 
                                  : 'opacity-40 cursor-not-allowed'
                              }`}
                              onClick={() => message.metadata?.audio_url && console.log('Play audio:', message.metadata.audio_url)}
                              disabled={!message.metadata?.audio_url}
                              title={message.metadata?.audio_url ? "Play voice message" : "Audio not available"}
                            >
                              <Play className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                        <p className={`text-xs mt-1 ${
                          message.role === 'user' 
                            ? 'text-primary-foreground/70 text-right' 
                            : 'text-muted-foreground text-left'
                        }`}>
                          {message.created_at ? format(new Date(message.created_at), "HH:mm") : ""}
                        </p>
                        {/* Chat bubble tail */}
                        {message.role === 'user' ? (
                          <div className="absolute right-0 top-2 w-0 h-0 border-l-[6px] border-l-primary border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent translate-x-1.5"></div>
                        ) : (
                          <div className="absolute left-0 top-2 w-0 h-0 border-r-[6px] border-r-muted border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent -translate-x-1.5"></div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-center pt-2 border-t">
                  <button
                    onClick={() => router.push(`/conversations/${userId}`)}
                    className="text-sm text-primary hover:text-primary/80 font-medium flex items-center gap-1"
                  >
                    <Eye className="w-4 h-4" />
                    View Full History
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="w-12 h-12 text-muted-foreground/50 mx-auto mb-2" />
                <p className="text-muted-foreground">No messages yet</p>
                <p className="text-xs text-muted-foreground mt-1">User hasn't sent any messages</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Memory Facts</CardTitle>
                <CardDescription>Learned information about this user</CardDescription>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => router.push(`/memory/facts?userId=${userId}`)}
              >
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {factsLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              </div>
            ) : facts?.length ? (
              <DataTable
                columns={factColumns}
                data={facts.slice(0, 5)}
                pageSize={5}
              />
            ) : (
              <p className="text-muted-foreground text-center py-8">No facts stored yet</p>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}