import { useState, useEffect } from 'react';
import { Configuration, UsersApi, ConversationsApi, VoiceApi, MemoryApi, HealthApi } from '@privet/api-client';

export interface ApiConfig {
  basePath?: string;
  accessToken?: string;
}

export function useApi(config?: ApiConfig) {
  const [apiConfig] = useState(() => new Configuration({
    basePath: config?.basePath || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    accessToken: config?.accessToken,
  }));

  return {
    users: new UsersApi(apiConfig),
    conversations: new ConversationsApi(apiConfig),
    voice: new VoiceApi(apiConfig),
    memory: new MemoryApi(apiConfig),
    health: new HealthApi(apiConfig),
  };
}

export function useApiHealth() {
  const api = useApi();
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.health.healthStatusApiV1HealthStatusGet();
        setIsHealthy(true);
      } catch {
        setIsHealthy(false);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return { isHealthy, loading };
}