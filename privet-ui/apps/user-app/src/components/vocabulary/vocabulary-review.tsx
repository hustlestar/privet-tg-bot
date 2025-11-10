/**
 * VocabularyReview Component
 *
 * Flashcard-style review interface with spaced repetition
 */

'use client';

import { useState, useEffect } from 'react';
import { Check, X, Volume2, RefreshCw, Award } from 'lucide-react';
import type { VocabularyWord } from '../../types/vocabulary';
import { useWordReview, usePronunciation } from '../../hooks/useVocabulary';

interface VocabularyReviewProps {
  userId: number;
  reviewType?: 'all' | 'due' | 'mastered' | 'learning';
  onComplete?: () => void;
}

export function VocabularyReview({
  userId,
  reviewType = 'due',
  onComplete,
}: VocabularyReviewProps) {
  const [words, setWords] = useState<VocabularyWord[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [sessionStats, setSessionStats] = useState({ correct: 0, incorrect: 0, total: 0 });
  const [isComplete, setIsComplete] = useState(false);

  const { reviewWord, getWordsForReview, loading } = useWordReview();
  const { playWord, isPlaying } = usePronunciation();

  useEffect(() => {
    loadWords();
  }, [userId, reviewType]);

  const loadWords = async () => {
    try {
      const response = await getWordsForReview(userId, {
        limit: 20,
        review_type: reviewType,
      });
      setWords(response.words);
      setCurrentIndex(0);
      setShowAnswer(false);
      setIsComplete(false);
      setSessionStats({ correct: 0, incorrect: 0, total: 0 });
    } catch (error) {
      console.error('Failed to load words for review:', error);
    }
  };

  const handleReview = async (wasCorrect: boolean) => {
    const currentWord = words[currentIndex];
    if (!currentWord) return;

    try {
      await reviewWord({
        word_id: currentWord.id,
        user_id: userId,
        was_correct: wasCorrect,
        review_type: 'flashcard',
      });

      setSessionStats((prev) => ({
        correct: prev.correct + (wasCorrect ? 1 : 0),
        incorrect: prev.incorrect + (wasCorrect ? 0 : 1),
        total: prev.total + 1,
      }));

      // Move to next word
      if (currentIndex < words.length - 1) {
        setCurrentIndex((i) => i + 1);
        setShowAnswer(false);
      } else {
        setIsComplete(true);
      }
    } catch (error) {
      console.error('Failed to record review:', error);
    }
  };

  const handlePlayPronunciation = async () => {
    const currentWord = words[currentIndex];
    if (!currentWord) return;

    try {
      await playWord({
        text: currentWord.word_text,
        language_code: currentWord.target_language,
      });
    } catch (error) {
      console.error('Failed to play pronunciation:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading review session...</p>
        </div>
      </div>
    );
  }

  if (words.length === 0) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-200 dark:border-gray-700">
          <Award className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            No words to review
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {reviewType === 'due'
              ? "You're all caught up! Come back later for more reviews."
              : 'Add more words to your vocabulary to start reviewing.'}
          </p>
          <button
            onClick={() => onComplete?.()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            Back to Vocabulary
          </button>
        </div>
      </div>
    );
  }

  if (isComplete) {
    const accuracy = sessionStats.total > 0
      ? Math.round((sessionStats.correct / sessionStats.total) * 100)
      : 0;

    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-200 dark:border-gray-700">
          <Award className="w-20 h-20 mx-auto text-green-500 mb-6" />
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Review Complete!
          </h2>

          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                {sessionStats.correct}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Correct</p>
            </div>

            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                {sessionStats.incorrect}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Incorrect</p>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{accuracy}%</p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Accuracy</p>
            </div>
          </div>

          <div className="flex gap-4 justify-center">
            <button
              onClick={loadWords}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Review Again
            </button>

            <button
              onClick={() => onComplete?.()}
              className="px-6 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors"
            >
              Back to Vocabulary
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentWord = words[currentIndex];
  const progress = ((currentIndex + 1) / words.length) * 100;

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>Progress</span>
          <span>
            {currentIndex + 1} / {words.length}
          </span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Flashcard */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-12 min-h-[400px] flex flex-col items-center justify-center">
          {/* Question Side */}
          {!showAnswer && (
            <div className="text-center w-full">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                What does this word mean?
              </p>
              <h2 className="text-5xl font-bold text-gray-900 dark:text-white mb-8">
                {currentWord.word_text}
              </h2>

              {currentWord.part_of_speech && (
                <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
                  {currentWord.part_of_speech}
                  {currentWord.difficulty_level && ` • ${currentWord.difficulty_level}`}
                </p>
              )}

              <button
                onClick={handlePlayPronunciation}
                disabled={isPlaying}
                className="mx-auto mb-8 p-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-full transition-colors"
              >
                <Volume2 className="w-6 h-6" />
              </button>

              <button
                onClick={() => setShowAnswer(true)}
                className="px-8 py-4 bg-gray-900 dark:bg-gray-700 hover:bg-gray-800 dark:hover:bg-gray-600 text-white rounded-lg font-medium text-lg transition-colors"
              >
                Show Answer
              </button>
            </div>
          )}

          {/* Answer Side */}
          {showAnswer && (
            <div className="text-center w-full">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                {currentWord.word_text}
              </h2>

              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 mb-8">
                <p className="text-2xl text-gray-900 dark:text-white font-medium">
                  {currentWord.translation}
                </p>
              </div>

              {currentWord.example_sentence && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-8 text-left">
                  <p className="text-gray-700 dark:text-gray-300 italic mb-2">
                    "{currentWord.example_sentence}"
                  </p>
                  {currentWord.example_translation && (
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      → {currentWord.example_translation}
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => handleReview(false)}
                  className="px-8 py-4 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-lg transition-colors flex items-center gap-2"
                >
                  <X className="w-6 h-6" />
                  Incorrect
                </button>

                <button
                  onClick={() => handleReview(true)}
                  className="px-8 py-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-lg transition-colors flex items-center gap-2"
                >
                  <Check className="w-6 h-6" />
                  Correct
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-600 dark:text-gray-400">
        <div className="flex items-center gap-2">
          <Check className="w-5 h-5 text-green-500" />
          <span>{sessionStats.correct} correct</span>
        </div>
        <div className="flex items-center gap-2">
          <X className="w-5 h-5 text-red-500" />
          <span>{sessionStats.incorrect} incorrect</span>
        </div>
      </div>
    </div>
  );
}
