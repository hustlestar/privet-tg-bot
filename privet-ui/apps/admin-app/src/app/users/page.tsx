"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button } from "@privet-ui/shared";
import { Users, UserPlus, Search, Download, RefreshCw } from "lucide-react";
import { DataTable } from "@/components/ui/data-table";
import { useAdminApi } from "@/hooks/useApi";
import { ColumnDef } from "@tanstack/react-table";
import type { User } from "@privet/api-client";
import { useRouter } from "next/navigation";
import { format } from "date-fns";

export default function UsersPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const pageSize = 20;

  const { useUsers, useDeleteUser } = useAdminApi();
  const { data, isLoading, refetch } = useUsers(currentPage * pageSize, pageSize);
  const deleteUser = useDeleteUser();

  const columns: ColumnDef<User>[] = [
    {
      accessorKey: "user_id",
      header: "ID",
      cell: ({ row }) => (
        <div className="font-mono text-xs">{row.getValue("user_id")}</div>
      ),
    },
    {
      accessorKey: "username",
      header: "Username",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("username") || "—"}</div>
      ),
    },
    {
      accessorKey: "first_name",
      header: "Name",
      cell: ({ row }) => {
        const firstName = row.original.first_name;
        const lastName = row.original.last_name;
        return (
          <div>
            {firstName || lastName ? `${firstName || ""} ${lastName || ""}`.trim() : "—"}
          </div>
        );
      },
    },
    {
      accessorKey: "language",
      header: "Language",
      cell: ({ row }) => (
        <div className="uppercase text-xs bg-muted px-2 py-1 rounded w-fit">
          {row.getValue("language") || "en"}
        </div>
      ),
    },
    {
      accessorKey: "created_at",
      header: "Joined",
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
      accessorKey: "is_active",
      header: "Status",
      cell: ({ row }) => {
        const isActive = row.getValue("is_active");
        return (
          <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            isActive ? "bg-success/10 text-success" : "bg-muted text-muted-foreground"
          }`}>
            {isActive ? "Active" : "Inactive"}
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
              router.push(`/users/${row.original.user_id}`);
            }}
          >
            View
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={(e) => {
              e.stopPropagation();
              if (confirm("Are you sure you want to delete this user?")) {
                deleteUser.mutate(row.original.user_id);
              }
            }}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  const filteredUsers = data?.items?.filter((user: User) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      user.username?.toLowerCase().includes(term) ||
      user.first_name?.toLowerCase().includes(term) ||
      user.last_name?.toLowerCase().includes(term) ||
      user.user_id.toString().includes(term)
    );
  }) || [];

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
              <Users className="w-8 h-8" />
              User Management
            </h1>
            <p className="text-muted-foreground">
              Manage and monitor all registered users
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button>
              <UserPlus className="w-4 h-4 mr-2" />
              Add User
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
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.total || 0}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-success">
              {filteredUsers.filter((u: User) => u.is_active).length}
            </div>
            <p className="text-xs text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">New Today</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-info">
              {filteredUsers.filter((u: User) => {
                const today = new Date().toDateString();
                return u.created_at && new Date(u.created_at).toDateString() === today;
              }).length}
            </div>
            <p className="text-xs text-muted-foreground">Joined today</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Languages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(filteredUsers.map((u: User) => u.language || "en")).size}
            </div>
            <p className="text-xs text-muted-foreground">Unique languages</p>
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
                <CardTitle>Users</CardTitle>
                <CardDescription>
                  A list of all users registered in the system
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <Button variant="outline">
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
            ) : (
              <DataTable
                columns={columns}
                data={filteredUsers}
                pageSize={pageSize}
                onRowClick={(user) => router.push(`/users/${user.user_id}`)}
              />
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}