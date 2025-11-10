/**
 * VocabularyList Component
 *
 * Displays user's saved vocabulary with:
 * - Filtering by language and mastery level
 * - Pagination
 * - Review interface with spaced repetition
 * - Progress tracking
 */

'use client';

import { useState, useEffect } from 'react';
import { Search, Filter, Star, Clock, TrendingUp, Volume2, Trash2 } from 'lucide-react';
import type { VocabularyWord } from '../../types/vocabulary';
import { useVocabularyWords, useVocabularyStats, usePronunciation } from '../../hooks/useVocabulary';

interface VocabularyListProps {
  userId: number;
  targetLanguage?: string;
  nativeLanguage?: string;
}

export function VocabularyList({ userId, targetLanguage, nativeLanguage }: VocabularyListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLevel, setFilterLevel] = useState<'all' | 'learning' | 'mastered'>('all');
  const [currentPage, setCurrentPage] = useState(0);
  const pageSize = 20;

  const { words, total, loading, fetchWords } = useVocabularyWords(userId);
  const { stats, fetchStats } = useVocabularyStats(userId);
  const { playWord, isPlaying } = usePronunciation();

  useEffect(() => {
    fetchWords({
      target_language: targetLanguage,
      offset: currentPage * pageSize,
      limit: pageSize,
    });
    fetchStats();
  }, [currentPage, targetLanguage, fetchWords, fetchStats]);

  const filteredWords = words.filter((word) => {
    // Search filter
    if (searchQuery && !word.word_text.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !word.translation?.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }

    // Mastery filter
    if (filterLevel === 'learning' && word.mastery_level >= 4) return false;
    if (filterLevel === 'mastered' && word.mastery_level < 4) return false;

    return true;
  });

  const handlePlayPronunciation = async (word: VocabularyWord) => {
    try {
      await playWord({
        text: word.word_text,
        language_code: word.target_language,
      });
    } catch (error) {
      console.error('Failed to play pronunciation:', error);
    }
  };

  const renderMasteryStars = (level: number) => {
    return (
      <div className="flex gap-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-4 h-4 ${
              i < level
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300 dark:text-gray-600'
            }`}
          />
        ))}
      </div>
    );
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header with Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            My Vocabulary
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {total} words • {stats?.learning_words || 0} learning • {stats?.mastered_words || 0} mastered
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Words</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {stats.total_words}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Learning</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {stats.learning_words}
                </p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Mastered</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {stats.mastered_words}
                </p>
              </div>
              <Star className="w-8 h-8 text-yellow-500 fill-yellow-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Due for Review</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {stats.due_for_review}
                </p>
              </div>
              <Filter className="w-8 h-8 text-green-500" />
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search words or translations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter by mastery */}
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Words</option>
            <option value="learning">Learning</option>
            <option value="mastered">Mastered</option>
          </select>
        </div>
      </div>

      {/* Word List */}
      <div className="space-y-3">
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading vocabulary...</p>
          </div>
        )}

        {!loading && filteredWords.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <p className="text-gray-600 dark:text-gray-400 text-lg">No words found</p>
            <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">
              {searchQuery
                ? 'Try a different search query'
                : 'Start adding words from conversations to build your vocabulary'}
            </p>
          </div>
        )}

        {!loading &&
          filteredWords.map((word) => (
            <div
              key={word.id}
              className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-4">
                {/* Word Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                      {word.word_text}
                    </h3>
                    {word.difficulty_level && (
                      <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium rounded">
                        {word.difficulty_level}
                      </span>
                    )}
                    {renderMasteryStars(word.mastery_level)}
                  </div>

                  {word.translation && (
                    <p className="text-lg text-gray-700 dark:text-gray-300 mb-2">
                      {word.translation}
                    </p>
                  )}

                  {word.part_of_speech && (
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {word.part_of_speech}
                    </p>
                  )}

                  {word.example_sentence && (
                    <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <p className="text-sm text-gray-700 dark:text-gray-300 italic">
                        "{word.example_sentence}"
                      </p>
                      {word.example_translation && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          → {word.example_translation}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Progress Info */}
                  <div className="flex items-center gap-4 mt-3 text-xs text-gray-500 dark:text-gray-400">
                    <span>
                      Reviewed {word.times_reviewed} times • {word.times_correct} correct
                    </span>
                    {word.next_review_at && (
                      <span>
                        Next review: {new Date(word.next_review_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => handlePlayPronunciation(word)}
                    disabled={isPlaying}
                    className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg transition-colors"
                    title="Play pronunciation"
                  >
                    <Volume2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
            disabled={currentPage === 0}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>

          <span className="px-4 py-2 text-gray-700 dark:text-gray-300">
            Page {currentPage + 1} of {totalPages}
          </span>

          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={currentPage >= totalPages - 1}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
