/**
 * InteractiveMessage Component
 *
 * Enhanced message component that wraps words with InteractiveWord for learning
 */

'use client';

import { motion } from 'framer-motion';
import { cn } from '@privet-ui/shared';
import { User, Bot, Heart, Smile, Frown, Zap, Sparkles } from 'lucide-react';
import { useMemo, useState, useEffect } from 'react';
import { InteractiveWord } from '../vocabulary/interactive-word';
import { useWordExtraction } from '../../hooks/useVocabulary';
import type { ExtractedWord, InteractiveWordData } from '../../types/vocabulary';

interface InteractiveMessageProps {
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  emotion?: string;
  userId: number;
  targetLanguage: string;
  nativeLanguage: string;
  enableInteractiveWords?: boolean;
}

const emotionIcons: Record<string, React.ReactNode> = {
  happy: <Smile className="w-4 h-4 text-yellow-500" />,
  sad: <Frown className="w-4 h-4 text-blue-500" />,
  love: <Heart className="w-4 h-4 text-red-500" />,
  excited: <Zap className="w-4 h-4 text-orange-500" />,
  neutral: <Sparkles className="w-4 h-4 text-gray-500" />,
};

/**
 * Parse text into words and non-word characters
 */
function parseTextIntoTokens(text: string): Array<{ text: string; isWord: boolean }> {
  const tokens: Array<{ text: string; isWord: boolean }> = [];
  const regex = /\b[\w'-]+\b/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    // Add text before the word (spaces, punctuation)
    if (match.index > lastIndex) {
      tokens.push({
        text: text.substring(lastIndex, match.index),
        isWord: false,
      });
    }

    // Add the word
    tokens.push({
      text: match[0],
      isWord: true,
    });

    lastIndex = regex.lastIndex;
  }

  // Add any remaining text
  if (lastIndex < text.length) {
    tokens.push({
      text: text.substring(lastIndex),
      isWord: false,
    });
  }

  return tokens;
}

export function InteractiveMessage({
  content,
  role,
  timestamp,
  emotion,
  userId,
  targetLanguage,
  nativeLanguage,
  enableInteractiveWords = true,
}: InteractiveMessageProps) {
  const isUser = role === 'user';
  const [extractedWords, setExtractedWords] = useState<Map<string, ExtractedWord>>(new Map());
  const { extractWords } = useWordExtraction();

  useEffect(() => {
    // Only extract words for assistant messages in target language
    if (!isUser && enableInteractiveWords && role === 'assistant') {
      extractWords({
        text: content,
        target_language: targetLanguage,
        native_language: nativeLanguage,
        user_id: userId,
        max_words: 20,
      })
        .then((response) => {
          const wordMap = new Map<string, ExtractedWord>();
          response.extracted_words.forEach((word) => {
            wordMap.set(word.word.toLowerCase(), word);
          });
          setExtractedWords(wordMap);
        })
        .catch((error) => {
          console.error('Failed to extract words:', error);
        });
    }
  }, [content, isUser, enableInteractiveWords, targetLanguage, nativeLanguage, userId, extractWords, role]);

  const renderedContent = useMemo(() => {
    if (isUser || !enableInteractiveWords || extractedWords.size === 0) {
      return <p className="text-sm whitespace-pre-wrap">{content}</p>;
    }

    const tokens = parseTextIntoTokens(content);

    return (
      <p className="text-sm whitespace-pre-wrap">
        {tokens.map((token, index) => {
          if (!token.isWord) {
            return <span key={index}>{token.text}</span>;
          }

          const wordData = extractedWords.get(token.text.toLowerCase());

          if (wordData) {
            const interactiveData: InteractiveWordData = {
              word: token.text,
              translation: wordData.translation,
              part_of_speech: wordData.part_of_speech,
              difficulty_level: wordData.difficulty_level,
              pronunciation_cache_id: null,
              is_known: wordData.is_known,
              can_pronounce: true,
            };

            return (
              <InteractiveWord
                key={index}
                word={token.text}
                data={interactiveData}
                targetLanguage={targetLanguage}
                nativeLanguage={nativeLanguage}
                userId={userId}
              />
            );
          }

          return <span key={index}>{token.text}</span>;
        })}
      </p>
    );
  }, [content, isUser, enableInteractiveWords, extractedWords, targetLanguage, nativeLanguage, userId]);

  return (
    <motion.div
      className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}
      initial={{ opacity: 0, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-secondary'
        )}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </motion.div>

      <motion.div
        className={cn('flex flex-col gap-1 max-w-[70%]', isUser ? 'items-end' : 'items-start')}
        layout
      >
        <motion.div
          className={cn(
            'rounded-2xl px-4 py-2',
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground'
          )}
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        >
          {renderedContent}
        </motion.div>

        <div className="flex items-center gap-2 px-2">
          <span className="text-xs text-muted-foreground">
            {timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          {emotion && !isUser && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="flex items-center gap-1"
            >
              {emotionIcons[emotion] || emotionIcons.neutral}
            </motion.span>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
