/**
 * TypeScript types for vocabulary and language learning features
 */

export interface VocabularyWord {
  id: number;
  user_id: number;
  word_text: string;
  normalized_form: string;
  target_language: string;
  native_language: string;
  translation: string | null;
  part_of_speech: string | null;
  difficulty_level: string | null;
  example_sentence: string | null;
  example_translation: string | null;
  pronunciation_ipa: string | null;
  pronunciation_cache_id: number | null;
  pronunciation_url: string | null;
  added_from_message_id: number | null;
  metadata: Record<string, any> | null;
  times_reviewed: number;
  times_correct: number;
  mastery_level: number;
  is_active: boolean;
  last_reviewed_at: string | null;
  next_review_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExtractedWord {
  word: string;
  translation: string;
  part_of_speech: string | null;
  difficulty_level: string | null;
  context: string | null;
  is_known: boolean;
}

export interface WordExtractionRequest {
  text: string;
  target_language: string;
  native_language: string;
  user_id?: number;
  max_words?: number;
}

export interface WordExtractionResponse {
  extracted_words: ExtractedWord[];
  total_words: number;
  unique_words: number;
}

export interface VocabularyWordCreate {
  user_id: number;
  word_text: string;
  target_language: string;
  native_language: string;
  translation?: string;
  part_of_speech?: string;
  difficulty_level?: string;
  example_sentence?: string;
  example_translation?: string;
  added_from_message_id?: number;
}

export interface WordReviewRequest {
  word_id: number;
  user_id: number;
  was_correct: boolean;
  review_type?: string;
}

export interface WordReviewResponse {
  word_id: number;
  new_mastery_level: number;
  next_review_at: string | null;
  xp_earned: number;
}

export interface WordsForReviewResponse {
  words: VocabularyWord[];
  total_due: number;
  total_learning: number;
  total_mastered: number;
}

export interface VocabularyStats {
  total_words: number;
  mastered_words: number;
  learning_words: number;
  due_for_review: number;
  avg_mastery: number;
}

export interface PronunciationRequest {
  text: string;
  language_code: string;
  voice_id?: string;
  use_cache?: boolean;
}

export interface PronunciationResponse {
  text: string;
  language_code: string;
  audio_data: string; // base64 encoded
  audio_format: string;
  from_cache: boolean;
  cache_id: number | null;
  voice_id: string;
  provider: string;
}

export interface AdvancedTranslationRequest {
  word: string;
  source_language: string;
  target_language: string;
  context?: string;
}

export interface AdvancedTranslationResponse {
  word: string;
  translations: string[];
  definitions: string[];
  examples: Array<{
    sentence: string;
    translation: string;
  }>;
  synonyms: string[];
  antonyms: string[];
  conjugations: Record<string, any> | null;
  etymology: string | null;
  usage_notes: string | null;
  stub_message: string;
}

export interface InteractiveWordData {
  word: string;
  translation: string | null;
  part_of_speech: string | null;
  difficulty_level: string | null;
  pronunciation_cache_id: number | null;
  is_known: boolean;
  can_pronounce: boolean;
}
