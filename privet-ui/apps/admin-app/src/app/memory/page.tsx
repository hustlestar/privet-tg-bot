"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button } from "@privet-ui/shared";
import { Brain, Search, Plus, Download, RefreshCw, Trash2, Edit, Filter } from "lucide-react";
import { DataTable } from "@/components/ui/data-table";
import { useAdminApi } from "@/hooks/useApi";
import { ColumnDef } from "@tanstack/react-table";
import type { UserFact } from "@privet/api-client";
import { useRouter } from "next/navigation";
import { format } from "date-fns";

export default function MemoryPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUserId, setSelectedUserId] = useState<number | undefined>();
  const [selectedCategory, setSelectedCategory] = useState("");

  const { useUsers, useUserFacts, useDeleteFact } = useAdminApi();
  const { data: usersData } = useUsers(0, 1000);
  const { data: facts, isLoading, refetch } = useUserFacts(
    selectedUserId || 0,
    100,
    0,
    selectedCategory || undefined
  );
  const deleteFact = useDeleteFact();

  const columns: ColumnDef<UserFact>[] = [
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
          <div>
            <div className="font-medium">
              {user?.first_name || user?.last_name 
                ? `${user.first_name || ""} ${user.last_name || ""}`.trim()
                : user?.username || `User ${userId}`}
            </div>
            <div className="text-xs text-muted-foreground">ID: {userId}</div>
          </div>
        );
      },
    },
    {
      accessorKey: "fact_text",
      header: "Fact",
      cell: ({ row }) => (
        <div className="max-w-md">
          <div className="line-clamp-3">{row.getValue("fact_text")}</div>
        </div>
      ),
    },
    {
      accessorKey: "category",
      header: "Category",
      cell: ({ row }) => (
        <div className="text-xs bg-muted px-2 py-1 rounded w-fit">
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
            {date ? format(new Date(date), "MMM d, yyyy") : "—"}
          </div>
        );
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Implement edit fact
            }}
          >
            <Edit className="w-3 h-3" />
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={(e) => {
              e.stopPropagation();
              if (confirm("Are you sure you want to delete this fact?")) {
                deleteFact.mutate(row.original.id);
              }
            }}
          >
            <Trash2 className="w-3 h-3" />
          </Button>
        </div>
      ),
    },
  ];

  const filteredFacts = facts?.filter((fact: UserFact) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      fact.fact_text?.toLowerCase().includes(term) ||
      fact.category?.toLowerCase().includes(term) ||
      fact.user_id.toString().includes(term)
    );
  }) || [];

  const categories = Array.from(new Set(facts?.map(f => f.category).filter(Boolean))) as string[];

  const stats = {
    totalFacts: facts?.length || 0,
    uniqueUsers: new Set(facts?.map(f => f.user_id)).size || 0,
    categories: categories.length,
    todayFacts: facts?.filter(f => 
      f.created_at && new Date(f.created_at).toDateString() === new Date().toDateString()
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
              <Brain className="w-8 h-8" />
              Memory & RAG System
            </h1>
            <p className="text-muted-foreground">
              Manage user facts, knowledge base, and memory context
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Fact
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
            <CardTitle className="text-sm font-medium">Total Facts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalFacts}</div>
            <p className="text-xs text-muted-foreground">Stored memories</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Users with Facts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{stats.uniqueUsers}</div>
            <p className="text-xs text-muted-foreground">Have memories</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Categories</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-info">{stats.categories}</div>
            <p className="text-xs text-muted-foreground">Fact categories</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Added Today</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-success">{stats.todayFacts}</div>
            <p className="text-xs text-muted-foreground">New facts</p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid gap-6 lg:grid-cols-3"
      >
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>User Facts Database</CardTitle>
                <CardDescription>
                  Manage learned information about users
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <select
                  value={selectedUserId || ""}
                  onChange={(e) => setSelectedUserId(e.target.value ? parseInt(e.target.value) : undefined)}
                  className="px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                >
                  <option value="">All Users</option>
                  {usersData?.items?.map((user) => (
                    <option key={user.user_id} value={user.user_id}>
                      {user.first_name || user.last_name 
                        ? `${user.first_name || ""} ${user.last_name || ""}`.trim()
                        : user.username || `User ${user.user_id}`}
                    </option>
                  ))}
                </select>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search facts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  />
                </div>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
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
                <Brain className="w-12 h-12 mb-4" />
                <h3 className="text-lg font-medium mb-2">Select a User</h3>
                <p>Choose a user to view their stored facts and memories</p>
              </div>
            ) : filteredFacts.length > 0 ? (
              <DataTable
                columns={columns}
                data={filteredFacts}
                pageSize={10}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                <Brain className="w-12 h-12 mb-4" />
                <h3 className="text-lg font-medium mb-2">No Facts Found</h3>
                <p>No facts match the current filters</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Category Breakdown</CardTitle>
            <CardDescription>Distribution of fact categories</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {categories.length > 0 ? (
                categories.map((category) => {
                  const count = facts?.filter(f => f.category === category).length || 0;
                  const percentage = stats.totalFacts > 0 ? (count / stats.totalFacts) * 100 : 0;
                  
                  return (
                    <div key={category} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{category}</span>
                        <span className="text-muted-foreground">{count} facts</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Brain className="w-8 h-8 mx-auto mb-2" />
                  <p>No categories yet</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="grid gap-6 lg:grid-cols-2"
      >
        <Card>
          <CardHeader>
            <CardTitle>Memory Search</CardTitle>
            <CardDescription>Test semantic search across user facts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter search query..."
                  className="flex-1 px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <Button>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </div>
              <div className="text-sm text-muted-foreground">
                Search will return semantically similar facts using vector embeddings
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>RAG Statistics</CardTitle>
            <CardDescription>Memory system performance metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm">Vector Dimension</span>
                <span className="text-sm font-mono">1536</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Embedding Model</span>
                <span className="text-sm font-mono">text-embedding-3-small</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Search Method</span>
                <span className="text-sm font-mono">Cosine Similarity</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Index Status</span>
                <span className="text-sm text-success">Active</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}