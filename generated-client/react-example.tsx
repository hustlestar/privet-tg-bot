// Example: How to use the generated API client in React

import React, { useEffect, useState } from 'react';
import { Configuration, UsersApi, ConversationsApi, AudioApi } from './api';
import type { User, ConversationResponse } from './models';

// Configure the API client
const config = new Configuration({
  basePath: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  // Add authentication headers if needed
  // headers: {
  //   'Authorization': `Bearer ${token}`
  // }
});

// Create API instances
const usersApi = new UsersApi(config);
const conversationsApi = new ConversationsApi(config);
const audioApi = new AudioApi(config);

// Example React component
export const ExampleComponent: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Example: Get or create user
  const getOrCreateUser = async (telegramId: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await usersApi.getUserOrCreate({
        telegramId,
        username: 'example_user',
        firstName: 'John',
        lastName: 'Doe'
      });
      
      setUser(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Example: Send a message to the conversation
  const sendMessage = async (userId: string, message: string) => {
    try {
      const response = await conversationsApi.processMessage({
        userId,
        requestBody: {
          message,
          telegram_id: 123456789,
          voice_response: false
        }
      });
      
      console.log('Response:', response.data);
      return response.data;
    } catch (err) {
      console.error('Error sending message:', err);
      throw err;
    }
  };

  // Example: Process audio
  const processAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.ogg');
      
      const response = await audioApi.transcribeAudio({
        audio: audioBlob as any
      });
      
      console.log('Transcription:', response.data);
      return response.data;
    } catch (err) {
      console.error('Error processing audio:', err);
      throw err;
    }
  };

  useEffect(() => {
    // Example: Load user on component mount
    getOrCreateUser(123456789);
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return null;

  return (
    <div>
      <h1>Welcome, {user.first_name}!</h1>
      <p>User ID: {user.id}</p>
      <button onClick={() => sendMessage(user.id, 'Hello from React!')}>
        Send Test Message
      </button>
    </div>
  );
};

// Custom React hook for the API
export const usePrivetApi = () => {
  const [config] = useState(() => new Configuration({
    basePath: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  }));

  return {
    users: new UsersApi(config),
    conversations: new ConversationsApi(config),
    audio: new AudioApi(config),
  };
};

// Usage in a component with the custom hook
export const AnotherExample: React.FC = () => {
  const api = usePrivetApi();
  
  const handleClick = async () => {
    try {
      const user = await api.users.getUserOrCreate({
        telegramId: 987654321,
        username: 'test_user'
      });
      console.log('User created:', user.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  return (
    <button onClick={handleClick}>
      Create Test User
    </button>
  );
};
