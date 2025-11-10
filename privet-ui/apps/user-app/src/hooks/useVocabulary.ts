/**
 * React hooks for vocabulary and pronunciation features
 */

import { useState, useCallback } from 'react';
import type {
  VocabularyWord,
  VocabularyWordCreate,
  WordExtractionRequest,
  WordReviewRequest,
  VocabularyStats,
  PronunciationRequest,
  AdvancedTranslationRequest,
} from '../types/vocabulary';
import * as vocabularyApi from '../lib/vocabulary-api';

// ===== Vocabulary Hooks =====

export function useVocabularyWords(userId: number) {
  const [words, setWords] = useState<VocabularyWord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWords = useCallback(
    async (params: { target_language?: string; offset?: number; limit?: number } = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await vocabularyApi.getUserVocabulary(userId, params);
        setWords(response.items);
        setTotal(response.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch vocabulary');
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  const addWord = useCallback(
    async (wordData: Omit<VocabularyWordCreate, 'user_id'>) => {
      setLoading(true);
      setError(null);

      try {
        const newWord = await vocabularyApi.addWordToVocabulary({
          ...wordData,
          user_id: userId,
        });

        // Add to local state
        setWords((prev) => [newWord, ...prev]);
        setTotal((prev) => prev + 1);

        return newWord;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to add word';
        setError(message);
        throw new Error(message);
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  return {
    words,
    total,
    loading,
    error,
    fetchWords,
    addWord,
  };
}

export function useWordExtraction() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const extractWords = useCallback(async (request: WordExtractionRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await vocabularyApi.extractWords(request);
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to extract words';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    extractWords,
    loading,
    error,
  };
}

export function useWordReview() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reviewWord = useCallback(async (review: WordReviewRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await vocabularyApi.reviewWord(review);
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to record review';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const getWordsForReview = useCallback(
    async (
      userId: number,
      params: { limit?: number; review_type?: 'all' | 'due' | 'mastered' | 'learning' } = {}
    ) => {
      setLoading(true);
      setError(null);

      try {
        const response = await vocabularyApi.getWordsForReview(userId, params);
        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to fetch words for review';
        setError(message);
        throw new Error(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    reviewWord,
    getWordsForReview,
    loading,
    error,
  };
}

export function useVocabularyStats(userId: number) {
  const [stats, setStats] = useState<VocabularyStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await vocabularyApi.getVocabularyStats(userId);
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  return {
    stats,
    loading,
    error,
    fetchStats,
  };
}

// ===== Pronunciation Hooks =====

export function usePronunciation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const playWord = useCallback(async (request: PronunciationRequest) => {
    setLoading(true);
    setError(null);
    setIsPlaying(true);

    try {
      const response = await vocabularyApi.synthesizePronunciation(request);

      // Play the audio
      await vocabularyApi.playAudioFromBase64(response.audio_data, response.audio_format);

      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to play pronunciation';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
      setIsPlaying(false);
    }
  }, []);

  const getAudioBlob = useCallback(async (request: PronunciationRequest) => {
    setLoading(true);
    setError(null);

    try {
      const blob = await vocabularyApi.synthesizePronunciationAudio(request);
      return blob;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get audio';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    playWord,
    getAudioBlob,
    loading,
    error,
    isPlaying,
  };
}

// ===== Advanced Translation Hook =====

export function useAdvancedTranslation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getAdvancedTranslation = useCallback(async (request: AdvancedTranslationRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await vocabularyApi.getAdvancedTranslation(request);
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch advanced translation';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    getAdvancedTranslation,
    loading,
    error,
  };
}
