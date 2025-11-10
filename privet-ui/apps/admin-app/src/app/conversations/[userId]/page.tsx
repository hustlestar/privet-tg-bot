"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button } from "@privet-ui/shared";
import { ArrowLeft, MessageSquare, Mic, Play, User, Bot, ChevronLeft, ChevronRight } from "lucide-react";
import { useAdminApi } from "@/hooks/useApi";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { DataTable } from "@/components/ui/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";

interface ConversationDetailPageProps {
  params: { userId: string };
}

interface ConversationMessage {
  id: number;
  role: string;
  message_text?: string;
  transcribed_text?: string;
  is_voice: boolean;
  created_at: string;
  metadata?: any;
}

export default function ConversationDetailPage({ params }: ConversationDetailPageProps) {
  const router = useRouter();
  const userId = parseInt(params.userId);
  const [currentPage, setCurrentPage] = useState(0);
  const messagesPerPage = 20;
  
  const { useUser, useConversationHistory } = useAdminApi();
  
  const { data: user, isLoading: userLoading } = useUser(userId);
  const { data: conversations, isLoading: conversationsLoading, error: conversationsError } = useConversationHistory(userId, messagesPerPage, currentPage * messagesPerPage);

  const totalMessages = conversations?.total || 0;
  const totalPages = Math.ceil(totalMessages / messagesPerPage);
  const hasNextPage = currentPage < totalPages - 1;
  const hasPrevPage = currentPage > 0;

  const conversationColumns: ColumnDef<ConversationMessage>[] = [
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => {
        const role = row.getValue("role") as string;
        return (
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${
            role === "user" 
              ? "bg-blue-50 text-blue-700 border-blue-200" 
              : "bg-green-50 text-green-700 border-green-200"
          }`}>
            {role === "user" ? (
              <User className="w-3 h-3" />
            ) : (
              <Bot className="w-3 h-3" />
            )}
            {role === "user" ? "User" : "Assistant"}
          </div>
        );
      },
    },
    {
      accessorKey: "message_text",
      header: "Message",
      cell: ({ row }) => {
        const messageText = row.getValue("message_text") as string;
        const transcribedText = row.original.transcribed_text;
        const isVoice = row.original.is_voice;
        
        return (
          <div className="max-w-md">
            {isVoice ? (
              <div className="flex items-center gap-2 p-2 bg-blue-50 rounded border">
                <Mic className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-blue-600 font-medium mb-1">Voice Message</div>
                  {transcribedText && (
                    <div className="text-sm">"{transcribedText}"</div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-sm leading-relaxed">{messageText || "No content"}</div>
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
          <div className="text-sm text-muted-foreground">
            {date ? format(new Date(date), "MMM d, yyyy HH:mm") : "—"}
          </div>
        );
      },
    },
  ];

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
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push(`/users/${userId}`)}>
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">
              Conversation History
            </h1>
            <p className="text-muted-foreground">
              Full conversation history for {user.first_name || user.last_name 
                ? `${user.first_name || ""} ${user.last_name || ""}`.trim()
                : user.username || `User ${user.user_id}`}
            </p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  Messages ({totalMessages} total)
                </CardTitle>
                <CardDescription>
                  Showing {messagesPerPage} messages per page • Page {currentPage + 1} of {totalPages || 1}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={!hasPrevPage}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={!hasNextPage}
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {conversationsLoading ? (
              <LoadingSpinner className="h-[400px]" text="Loading conversation history..." />
            ) : conversationsError ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-2">Unable to load conversation history</p>
                <p className="text-xs text-muted-foreground">There may be a connection issue with the API</p>
              </div>
            ) : conversations?.messages?.length ? (
              <div className="space-y-6">
                {/* Telegram-style chat view */}
                <div className="bg-muted/30 rounded-lg p-3 h-[700px] overflow-y-auto">
                  <div className="space-y-1">
                    {conversations.messages.map((message, index) => (
                      <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[70%] rounded-lg p-2 relative ${
                          message.role === 'user' 
                            ? 'bg-primary text-primary-foreground' 
                            : 'bg-card text-foreground border shadow-sm'
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
                            <div className="absolute left-0 top-2 w-0 h-0 border-r-[6px] border-r-card border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent -translate-x-1.5"></div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Additional pagination controls at bottom */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-4 pt-4 border-t">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={!hasPrevPage}
                    >
                      <ChevronLeft className="w-4 h-4 mr-2" />
                      Previous Page
                    </Button>
                    <span className="text-sm text-muted-foreground">
                      Page {currentPage + 1} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={!hasNextPage}
                    >
                      Next Page
                      <ChevronRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <EmptyState
                icon={MessageSquare}
                title="No Conversations"
                description="This user hasn't had any conversations yet"
                className="h-[400px]"
              />
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}