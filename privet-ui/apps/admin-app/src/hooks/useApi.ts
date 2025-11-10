import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApi as useApiBase } from "@privet-ui/shared";
import type { 
  User, 
  UserCreate, 
  UserUpdate,
  UserStats,
  ConversationRequest,
  ConversationHistory,
  UserFact,
  FactCreate,
  FactSearch,
  ProfileSummary,
  MemoryContext,
  MemoryStats
} from "@privet/api-client";

export function useAdminApi() {
  const api = useApiBase();
  const queryClient = useQueryClient();

  // ========== USER HOOKS ==========
  const useUsers = (offset = 0, limit = 20) => {
    return useQuery({
      queryKey: ["users", offset, limit],
      queryFn: async () => {
        const response = await api.users.listUsersApiV1UsersGet({ offset, limit });
        return response.data;
      },
    });
  };

  const useUser = (userId: number) => {
    return useQuery({
      queryKey: ["user", userId],
      queryFn: async () => {
        const response = await api.users.getUserApiV1UsersUserIdGet({ userId });
        return response.data;
      },
      enabled: !!userId,
    });
  };

  const useUserStats = (userId: number) => {
    return useQuery({
      queryKey: ["userStats", userId],
      queryFn: async () => {
        const response = await api.users.getUserStatsApiV1UsersUserIdStatsGet({ userId });
        return response.data;
      },
      enabled: !!userId,
    });
  };

  const useCreateUser = () => {
    return useMutation({
      mutationFn: async (userCreate: UserCreate) => {
        const response = await api.users.createUserApiV1UsersPost({ userCreate });
        return response.data;
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["users"] });
      },
    });
  };

  const useUpdateUser = () => {
    return useMutation({
      mutationFn: async ({ userId, userUpdate }: { userId: number; userUpdate: UserUpdate }) => {
        const response = await api.users.updateUserApiV1UsersUserIdPut({ userId, userUpdate });
        return response.data;
      },
      onSuccess: (data, variables) => {
        queryClient.invalidateQueries({ queryKey: ["user", variables.userId] });
        queryClient.invalidateQueries({ queryKey: ["users"] });
      },
    });
  };

  const useDeleteUser = () => {
    return useMutation({
      mutationFn: async (userId: number) => {
        const response = await api.users.deleteUserApiV1UsersUserIdDelete({ userId });
        return response.data;
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["users"] });
      },
    });
  };

  // ========== CONVERSATION HOOKS ==========
  const useConversationHistory = (userId: number, limit = 20, offset = 0) => {
    return useQuery({
      queryKey: ["conversationHistory", userId, limit, offset],
      queryFn: async () => {
        const response = await api.conversations.getConversationHistoryApiV1ConversationsUserIdHistoryGet({
          userId,
          limit,
          offset,
        });
        return response.data;
      },
      enabled: !!userId,
    });
  };

  const useProcessConversation = () => {
    return useMutation({
      mutationFn: async (request: ConversationRequest) => {
        const response = await api.conversations.processConversationApiV1ConversationsProcessPost({
          conversationRequest: request,
        });
        return response.data;
      },
      onSuccess: (data, variables) => {
        queryClient.invalidateQueries({ 
          queryKey: ["conversationHistory", variables.user_id] 
        });
      },
    });
  };

  const useDeleteConversation = () => {
    return useMutation({
      mutationFn: async ({ userId, messageId }: { userId: number; messageId: number }) => {
        const response = await api.conversations.deleteMessageApiV1ConversationsUserIdMessagesMessageIdDelete({
          userId,
          messageId,
        });
        return response.data;
      },
      onSuccess: (data, variables) => {
        queryClient.invalidateQueries({ 
          queryKey: ["conversationHistory", variables.userId] 
        });
      },
    });
  };

  // ========== MEMORY/RAG HOOKS ==========
  const useUserFacts = (userId: number, limit = 20, offset = 0, category?: string) => {
    return useQuery({
      queryKey: ["userFacts", userId, limit, offset, category],
      queryFn: async () => {
        const response = await api.memory.getUserFactsApiV1MemoryFactsUserIdGet({
          userId,
          limit,
          offset,
          category,
        });
        return response.data;
      },
      enabled: !!userId,
    });
  };

  const useCreateFact = () => {
    return useMutation({
      mutationFn: async (factCreate: FactCreate) => {
        const response = await api.memory.createFactApiV1MemoryFactsPost({
          factCreate,
        });
        return response.data;
      },
      onSuccess: (data, variables) => {
        queryClient.invalidateQueries({ 
          queryKey: ["userFacts", variables.user_id] 
        });
        queryClient.invalidateQueries({ 
          queryKey: ["memoryStats", variables.user_id] 
        });
      },
    });
  };

  const useSearchFacts = () => {
    return useMutation({
      mutationFn: async (search: FactSearch) => {
        const response = await api.memory.searchFactsApiV1MemoryFactsSearchPost({
          factSearch: search,
        });
        return response.data;
      },
    });
  };

  const useDeleteFact = () => {
    return useMutation({
      mutationFn: async (factId: number) => {
        const response = await api.memory.deleteFactApiV1MemoryFactsFactIdDelete({
          factId,
        });
        return response.data;
      },
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["userFacts"] });
        queryClient.invalidateQueries({ queryKey: ["memoryStats"] });
      },
    });
  };

  const useProfileSummaries = (userId: number) => {
    return useQuery({
      queryKey: ["profileSummaries", userId],
      queryFn: async () => {
        const response = await api.memory.getProfileSummariesApiV1MemorySummariesUserIdGet({
          userId,
        });
        return response.data;
      },
      enabled: !!userId,
    });
  };

  const useMemoryContext = (userId: number, query?: string) => {
    return useQuery({
      queryKey: ["memoryContext", userId, query],
      queryFn: async () => {
        const response = await api.memory.getMemoryContextApiV1MemoryContextUserIdGet({
          userId,
          query,
        });
        return response.data;
      },
      enabled: !!userId,
    });
  };

  const useMemoryStats = (userId: number) => {
    return useQuery({
      queryKey: ["memoryStats", userId],
      queryFn: async () => {
        const response = await api.memory.getMemoryStatsApiV1MemoryStatsUserIdGet({
          userId,
        });
        return response.data;
      },
      enabled: !!userId,
    });
  };

  // ========== VOICE HOOKS ==========
  const useTranscribeAudio = () => {
    return useMutation({
      mutationFn: async ({ audio, userId, language }: { 
        audio: File; 
        userId?: number; 
        language?: string 
      }) => {
        const response = await api.voice.transcribeAudioApiV1VoiceTranscribePost({
          audioFile: audio,
          userId,
          language,
        });
        return response.data;
      },
    });
  };

  const useSynthesizeSpeech = () => {
    return useMutation({
      mutationFn: async (request: any) => {
        const response = await api.voice.synthesizeSpeechApiV1VoiceSynthesizePost({
          synthesisRequest: request,
        });
        return response.data;
      },
    });
  };

  // ========== HEALTH HOOKS ==========
  const useHealthStatus = () => {
    return useQuery({
      queryKey: ["healthStatus"],
      queryFn: async () => {
        const response = await api.health.healthStatusApiV1HealthStatusGet();
        return response.data;
      },
      refetchInterval: 30000, // Check every 30 seconds
    });
  };

  // ========== EXPENSE HOOKS ==========
  const useCostBreakdown = (userId?: number, days = 30) => {
    return useQuery({
      queryKey: ["costBreakdown", userId, days],
      queryFn: async () => {
        const response = await api.expenses.getCostBreakdownApiV1ExpensesCostBreakdownGet({
          userId,
          days,
        });
        return response.data;
      },
    });
  };

  const useTotalCosts = (userId?: number, days = 30) => {
    return useQuery({
      queryKey: ["totalCosts", userId, days],
      queryFn: async () => {
        const response = await api.expenses.getTotalCostsApiV1ExpensesTotalCostsGet({
          userId,
          days,
        });
        return response.data;
      },
    });
  };

  const useUsageStats = (userId?: number, serviceType?: string, provider?: string, days = 30) => {
    return useQuery({
      queryKey: ["usageStats", userId, serviceType, provider, days],
      queryFn: async () => {
        const response = await api.expenses.getUsageStatsApiV1ExpensesUsageStatsGet({
          userId,
          serviceType,
          provider,
          days,
        });
        return response.data;
      },
    });
  };

  const useRecentUsage = (userId?: number, limit = 50) => {
    return useQuery({
      queryKey: ["recentUsage", userId, limit],
      queryFn: async () => {
        const response = await api.expenses.getRecentUsageApiV1ExpensesRecentUsageGet({
          userId,
          limit,
        });
        return response.data;
      },
    });
  };

  const useModelUsage = (days = 30) => {
    return useQuery({
      queryKey: ["modelUsage", days],
      queryFn: async () => {
        const response = await api.expenses.getModelUsageApiV1ExpensesModelsGet({
          days,
        });
        return response.data;
      },
    });
  };

  return {
    // User hooks
    useUsers,
    useUser,
    useUserStats,
    useCreateUser,
    useUpdateUser,
    useDeleteUser,
    
    // Conversation hooks
    useConversationHistory,
    useProcessConversation,
    useDeleteConversation,
    
    // Memory hooks
    useUserFacts,
    useCreateFact,
    useSearchFacts,
    useDeleteFact,
    useProfileSummaries,
    useMemoryContext,
    useMemoryStats,
    
    // Voice hooks
    useTranscribeAudio,
    useSynthesizeSpeech,
    
    // Health hooks
    useHealthStatus,
    
    // Expense hooks
    useCostBreakdown,
    useTotalCosts,
    useUsageStats,
    useRecentUsage,
    useModelUsage,
  };
}