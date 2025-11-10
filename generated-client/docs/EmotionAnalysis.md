# EmotionAnalysis

Emotion analysis result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **string** | Analyzed text | [default to undefined]
**sentiment_score** | **number** | Sentiment score | [default to undefined]
**primary_emotion** | [**EmotionType**](EmotionType.md) | Primary emotion | [default to undefined]
**confidence** | **number** | Confidence score | [default to undefined]
**emotions** | **{ [key: string]: number; }** | All emotion scores | [default to undefined]
**voice_tone_suggestion** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { EmotionAnalysis } from 'privet-api-client';

const instance: EmotionAnalysis = {
    text,
    sentiment_score,
    primary_emotion,
    confidence,
    emotions,
    voice_tone_suggestion,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
