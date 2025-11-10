/**
 * Vocabulary Demo Page
 *
 * Demonstrates all vocabulary learning features:
 * - InteractiveWord component
 * - VocabularyList with filtering
 * - VocabularyReview (flashcards)
 * - InteractiveMessage in chat context
 */

'use client';

import { useState } from 'react';
import { BookOpen, List, GraduationCap, MessageSquare } from 'lucide-react';
import { InteractiveWord } from '../../components/vocabulary/interactive-word';
import { VocabularyList } from '../../components/vocabulary/vocabulary-list';
import { VocabularyReview } from '../../components/vocabulary/vocabulary-review';
import { InteractiveMessage } from '../../components/chat/interactive-message';
import type { InteractiveWordData } from '../../types/vocabulary';

type Tab = 'word' | 'list' | 'review' | 'chat';

export default function VocabularyDemoPage() {
  const [activeTab, setActiveTab] = useState<Tab>('word');

  // Demo data for InteractiveWord
  const demoWordData: InteractiveWordData = {
    word: 'hola',
    translation: 'hello, hi',
    part_of_speech: 'interjection',
    difficulty_level: 'A1',
    pronunciation_cache_id: null,
    is_known: false,
    can_pronounce: true,
  };

  const tabs = [
    { id: 'word' as Tab, label: 'Interactive Word', icon: BookOpen },
    { id: 'list' as Tab, label: 'Vocabulary List', icon: List },
    { id: 'review' as Tab, label: 'Review Session', icon: GraduationCap },
    { id: 'chat' as Tab, label: 'Chat Integration', icon: MessageSquare },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Vocabulary Learning Demo
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Explore all language learning features
          </p>
        </div>

        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-2 overflow-x-auto pb-4">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap
                    ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'word' && (
          <div className="space-y-8">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Interactive Word Component
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Hover over the word for a quick translation, click to play audio and see details.
              </p>

              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-6">
                <p className="text-lg text-gray-900 dark:text-white">
                  Try clicking on this word:{' '}
                  <InteractiveWord
                    word="hola"
                    data={demoWordData}
                    targetLanguage="es"
                    nativeLanguage="en"
                    userId={1}
                  />
                  {' '}¿Cómo estás?
                </p>
              </div>

              <div className="mt-6 space-y-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
                    Features:
                  </h3>
                  <ul className="space-y-1 text-blue-800 dark:text-blue-300 text-sm">
                    <li>• Hover: Simple translation tooltip</li>
                    <li>• Click: Play pronunciation + show expanded popup</li>
                    <li>• "Add to Vocabulary" button (if not already known)</li>
                    <li>• "Advanced Translation" button (opens detailed modal)</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-6 border border-yellow-200 dark:border-yellow-800">
              <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-200 mb-2">
                ⚠️ Note: Backend Required
              </h3>
              <p className="text-yellow-800 dark:text-yellow-300">
                The interactive features require the backend API to be running. The pronunciation and
                "Add to Vocabulary" features will connect to the API endpoints at{' '}
                <code className="bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded">
                  http://localhost:8000
                </code>
              </p>
            </div>
          </div>
        )}

        {activeTab === 'list' && (
          <div>
            <VocabularyList userId={1} targetLanguage="es" nativeLanguage="en" />
          </div>
        )}

        {activeTab === 'review' && (
          <div>
            <VocabularyReview userId={1} reviewType="due" />
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Interactive Messages
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Words in assistant messages are automatically made interactive for learning.
              </p>

              <div className="space-y-4 max-w-3xl">
                <InteractiveMessage
                  content="Hello! How are you today?"
                  role="user"
                  timestamp={new Date()}
                  userId={1}
                  targetLanguage="en"
                  nativeLanguage="es"
                  enableInteractiveWords={false}
                />

                <InteractiveMessage
                  content="¡Hola! Estoy muy bien, gracias. ¿Y tú? ¿Cómo estás hoy?"
                  role="assistant"
                  timestamp={new Date()}
                  emotion="happy"
                  userId={1}
                  targetLanguage="es"
                  nativeLanguage="en"
                  enableInteractiveWords={true}
                />

                <InteractiveMessage
                  content="I'm learning Spanish!"
                  role="user"
                  timestamp={new Date()}
                  userId={1}
                  targetLanguage="en"
                  nativeLanguage="es"
                  enableInteractiveWords={false}
                />

                <InteractiveMessage
                  content="¡Excelente! El español es un idioma muy hermoso. ¿Qué te gusta más de aprender español?"
                  role="assistant"
                  timestamp={new Date()}
                  emotion="excited"
                  userId={1}
                  targetLanguage="es"
                  nativeLanguage="en"
                  enableInteractiveWords={true}
                />
              </div>

              <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
                  How it works:
                </h3>
                <ul className="space-y-1 text-blue-800 dark:text-blue-300 text-sm">
                  <li>
                    • Assistant messages are automatically parsed for vocabulary words
                  </li>
                  <li>• Each word becomes interactive (hover for translation, click for details)</li>
                  <li>• Known words are marked differently (lower opacity)</li>
                  <li>• User messages remain non-interactive for clean UX</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 border-t border-gray-200 dark:border-gray-700">
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            Getting Started
          </h3>
          <div className="space-y-2 text-gray-700 dark:text-gray-300 text-sm">
            <p>
              <strong>1. Start the backend:</strong>{' '}
              <code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                python -m privet_api.main
              </code>
            </p>
            <p>
              <strong>2. Run database migration:</strong> Apply the language learning tables
              migration
            </p>
            <p>
              <strong>3. Start the frontend:</strong>{' '}
              <code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                cd privet-ui && npm run dev
              </code>
            </p>
            <p>
              <strong>4. Test features:</strong> Try hovering and clicking words in the demo above
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
