"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button } from "@privet-ui/shared";
import { MessageSquare, Search, Filter, Download, RefreshCw, Calendar, User, Clock, Mic, Play } from "lucide-react";
import { DataTable } from "@/components/ui/data-table";
import { useAdminApi } from "@/hooks/useApi";
import { ColumnDef } from "@tanstack/react-table";
import type { ConversationMessage } from "@privet/api-client";
import { useRouter } from "next/navigation";
import { format } from "date-fns";

export default function ConversationsPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUserId, setSelectedUserId] = useState<number | undefined>();
  const [dateFilter, setDateFilter] = useState("");

  const { useUsers, useConversationHistory } = useAdminApi();
  const { data: usersData } = useUsers(0, 1000);
  const { data: conversations, isLoading, refetch, error } = useConversationHistory(
    selectedUserId || 0, 
    100, 
    0
  );

  const columns: ColumnDef<ConversationMessage>[] = [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <div className="font-mono text-xs">{row.getValue("id")}</div>
      ),
    },
    {
      accessorKey: "user_id",
      header: "User",
      cell: ({ row }) => {
        const userId = row.getValue("user_id") as number;
        const user = usersData?.items?.find(u => u.user_id === userId);
        return (
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-muted-foreground" />
            <div>
              <div className="font-medium">
                {user?.first_name || user?.last_name 
                  ? `${user.first_name || ""} ${user.last_name || ""}`.trim()
                  : user?.username || `User ${userId}`}
              </div>
              <div className="text-xs text-muted-foreground">ID: {userId}</div>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => (
        <div className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
          row.getValue("role") === "user" 
            ? "bg-primary/10 text-primary" 
            : "bg-secondary/50 text-secondary-foreground"
        }`}>
          {row.getValue("role") === "user" ? "User" : "Assistant"}
        </div>
      ),
    },
    {
      accessorKey: "message_text",
      header: "Message",
      cell: ({ row }) => {
        const messageText = row.getValue("message_text") as string;
        const transcribedText = row.original.transcribed_text;
        const isVoice = row.original.is_voice;
        const metadata = row.original.metadata;
        const audioUrl = metadata?.audio_url; // Check if audio URL is available in metadata
        
        return (
          <div className="max-w-md">
            {isVoice ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 p-2 bg-blue-50 rounded-lg border">
                  <Mic className="w-4 h-4 text-blue-600" />
                  <div className="flex-1">
                    <div className="text-xs text-blue-600 font-medium">Voice Message</div>
                    {transcribedText && (
                      <div className="text-sm font-medium">"{transcribedText}"</div>
                    )}
                  </div>
                  {audioUrl && (
                    <button 
                      className="p-1 hover:bg-blue-100 rounded-full transition-colors"
                      onClick={() => {
                        // TODO: Implement audio playback when audio URLs are available
                        console.log('Play audio:', audioUrl);
                      }}
                      title="Play voice message"
                    >
                      <Play className="w-4 h-4 text-blue-600" />
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="truncate">{messageText || "No content"}</div>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: "created_at",
      header: "Time",
      cell: ({ row }) => {
        const date = row.getValue("created_at") as string;
        return (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-3 h-3" />
            {date ? format(new Date(date), "MMM d, HH:mm:ss") : "—"}
          </div>
        );
      },
    },
  ];

  const filteredConversations = conversations?.messages?.filter((message: ConversationMessage) => {
    if (!searchTerm && !dateFilter) return true;
    
    const matchesSearch = !searchTerm || 
      message.content?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      message.user_id.toString().includes(searchTerm);
    
    const matchesDate = !dateFilter || 
      (message.created_at && new Date(message.created_at).toDateString() === new Date(dateFilter).toDateString());
    
    return matchesSearch && matchesDate;
  }) || [];

  const stats = {
    totalMessages: conversations?.messages?.length || 0,
    userMessages: conversations?.messages?.filter(m => m.role === "user").length || 0,
    assistantMessages: conversations?.messages?.filter(m => m.role === "assistant").length || 0,
    todayMessages: conversations?.messages?.filter(m => 
      m.created_at && new Date(m.created_at).toDateString() === new Date().toDateString()
    ).length || 0,
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <MessageSquare className="w-8 h-8" />
              Conversations
            </h1>
            <p className="text-muted-foreground">
              Monitor and analyze user conversations
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 md:grid-cols-4"
      >
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMessages}</div>
            <p className="text-xs text-muted-foreground">All conversations</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">User Messages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{stats.userMessages}</div>
            <p className="text-xs text-muted-foreground">From users</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Assistant Replies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-secondary">{stats.assistantMessages}</div>
            <p className="text-xs text-muted-foreground">AI responses</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Today's Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-success">{stats.todayMessages}</div>
            <p className="text-xs text-muted-foreground">Messages today</p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Conversation Messages</CardTitle>
                <CardDescription>
                  Monitor all user-bot interactions
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <select
                  value={selectedUserId || ""}
                  onChange={(e) => setSelectedUserId(e.target.value ? parseInt(e.target.value) : undefined)}
                  className="px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">All Users</option>
                  {usersData?.items?.map((user) => (
                    <option key={user.user_id} value={user.user_id}>
                      {user.first_name || user.last_name 
                        ? `${user.first_name || ""} ${user.last_name || ""}`.trim()
                        : user.username || `User ${user.user_id}`} (ID: {user.user_id})
                    </option>
                  ))}
                </select>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="date"
                    value={dateFilter}
                    onChange={(e) => setDateFilter(e.target.value)}
                    className="pl-10 pr-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search messages..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : !selectedUserId ? (
              <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                <MessageSquare className="w-12 h-12 mb-4" />
                <h3 className="text-lg font-medium mb-2">Select a User</h3>
                <p>Choose a user from the dropdown to view their conversations</p>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                <MessageSquare className="w-12 h-12 mb-4" />
                <h3 className="text-lg font-medium mb-2">Data Issue</h3>
                <p className="text-center">
                  Conversation data needs to be migrated to include message roles.<br/>
                  Please check the backend logs for migration instructions.
                </p>
              </div>
            ) : filteredConversations.length > 0 ? (
              <DataTable
                columns={columns}
                data={filteredConversations}
                pageSize={20}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                <MessageSquare className="w-12 h-12 mb-4" />
                <h3 className="text-lg font-medium mb-2">No Conversations</h3>
                <p>No messages found for the selected filters</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}