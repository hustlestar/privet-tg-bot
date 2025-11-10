/**
 * InteractiveWord Component
 *
 * UX Flow:
 * - Hover: Show simple translation tooltip
 * - Click: Play pronunciation + show expanded popup with details
 * - Advanced button: Open modal with advanced translation (stub)
 */

'use client';

import { useState } from 'react';
import { Volume2, BookOpen, Loader2 } from 'lucide-react';
import type { InteractiveWordData, AdvancedTranslationResponse } from '../../types/vocabulary';
import { usePronunciation, useAdvancedTranslation, useVocabularyWords } from '../../hooks/useVocabulary';

interface InteractiveWordProps {
  word: string;
  data: InteractiveWordData;
  targetLanguage: string;
  nativeLanguage: string;
  userId: number;
  onAddToVocabulary?: (word: string) => void;
}

export function InteractiveWord({
  word,
  data,
  targetLanguage,
  nativeLanguage,
  userId,
  onAddToVocabulary,
}: InteractiveWordProps) {
  const [showPopover, setShowPopover] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [advancedData, setAdvancedData] = useState<AdvancedTranslationResponse | null>(null);

  const { playWord, isPlaying } = usePronunciation();
  const { getAdvancedTranslation, loading: loadingAdvanced } = useAdvancedTranslation();
  const { addWord } = useVocabularyWords(userId);

  const handleClick = async () => {
    setShowPopover(true);

    // Play pronunciation if available
    if (data.can_pronounce) {
      try {
        await playWord({
          text: word,
          language_code: targetLanguage,
        });
      } catch (error) {
        console.error('Failed to play pronunciation:', error);
      }
    }
  };

  const handleAdvancedTranslation = async () => {
    try {
      const result = await getAdvancedTranslation({
        word: word,
        source_language: targetLanguage,
        target_language: nativeLanguage,
      });
      setAdvancedData(result);
      setShowAdvanced(true);
    } catch (error) {
      console.error('Failed to get advanced translation:', error);
    }
  };

  const handleAddToVocabulary = async () => {
    try {
      await addWord({
        word_text: word,
        target_language: targetLanguage,
        native_language: nativeLanguage,
        translation: data.translation || undefined,
        part_of_speech: data.part_of_speech || undefined,
        difficulty_level: data.difficulty_level || undefined,
      });

      onAddToVocabulary?.(word);
      setShowPopover(false);
    } catch (error) {
      console.error('Failed to add word to vocabulary:', error);
    }
  };

  return (
    <>
      {/* Main word with hover tooltip */}
      <span className="relative inline-block group">
        <button
          className={`
            text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300
            underline decoration-dotted underline-offset-4
            cursor-pointer transition-colors
            ${data.is_known ? 'opacity-60' : ''}
          `}
          onClick={handleClick}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          {word}
        </button>

        {/* Simple tooltip on hover */}
        {showTooltip && data.translation && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1.5 bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-lg shadow-lg whitespace-nowrap z-50 pointer-events-none">
            {data.translation}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700" />
          </div>
        )}
      </span>

      {/* Expanded popover on click */}
      {showPopover && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/20 backdrop-blur-sm"
            onClick={() => setShowPopover(false)}
          />

          {/* Popover content */}
          <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full p-6 space-y-4 animate-in fade-in duration-200">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  {word}
                  {isPlaying && (
                    <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                  )}
                </h3>
                {data.part_of_speech && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {data.part_of_speech}
                    {data.difficulty_level && ` • ${data.difficulty_level}`}
                  </p>
                )}
              </div>
              <button
                onClick={() => setShowPopover(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Translation */}
            {data.translation && (
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <p className="text-lg text-gray-900 dark:text-white font-medium">
                  {data.translation}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={() => playWord({ text: word, language_code: targetLanguage })}
                disabled={isPlaying || !data.can_pronounce}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
              >
                <Volume2 className="w-5 h-5" />
                {isPlaying ? 'Playing...' : 'Pronounce'}
              </button>

              {!data.is_known && (
                <button
                  onClick={handleAddToVocabulary}
                  className="px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
                >
                  Add to Vocabulary
                </button>
              )}
            </div>

            {/* Advanced Translation Button */}
            <button
              onClick={handleAdvancedTranslation}
              disabled={loadingAdvanced}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors"
            >
              <BookOpen className="w-5 h-5" />
              {loadingAdvanced ? 'Loading...' : 'Advanced Translation'}
            </button>
          </div>
        </div>
      )}

      {/* Advanced Translation Modal */}
      {showAdvanced && advancedData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setShowAdvanced(false)}
          />

          {/* Modal content */}
          <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {advancedData.word}
              </h2>
              <button
                onClick={() => setShowAdvanced(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Body - Scrollable */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Stub Message */}
              {advancedData.stub_message && (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    ⚠️ {advancedData.stub_message}
                  </p>
                </div>
              )}

              {/* Translations */}
              {advancedData.translations.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Translations
                  </h3>
                  <ul className="space-y-1">
                    {advancedData.translations.map((trans, idx) => (
                      <li key={idx} className="text-gray-700 dark:text-gray-300">
                        • {trans}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Definitions */}
              {advancedData.definitions.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Definitions
                  </h3>
                  <ul className="space-y-1">
                    {advancedData.definitions.map((def, idx) => (
                      <li key={idx} className="text-gray-700 dark:text-gray-300">
                        {idx + 1}. {def}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Examples */}
              {advancedData.examples.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Examples
                  </h3>
                  <div className="space-y-3">
                    {advancedData.examples.map((example, idx) => (
                      <div key={idx} className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                        <p className="text-gray-900 dark:text-white font-medium">
                          {example.sentence}
                        </p>
                        <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                          → {example.translation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Synonyms & Antonyms */}
              <div className="grid grid-cols-2 gap-4">
                {advancedData.synonyms.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                      Synonyms
                    </h3>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {advancedData.synonyms.join(', ')}
                    </p>
                  </div>
                )}
                {advancedData.antonyms.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                      Antonyms
                    </h3>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {advancedData.antonyms.join(', ')}
                    </p>
                  </div>
                )}
              </div>

              {/* Etymology & Usage Notes */}
              {advancedData.etymology && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    Etymology
                  </h3>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {advancedData.etymology}
                  </p>
                </div>
              )}

              {advancedData.usage_notes && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    Usage Notes
                  </h3>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {advancedData.usage_notes}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
