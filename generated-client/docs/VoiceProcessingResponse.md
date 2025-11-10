# VoiceProcessingResponse

Complete voice processing response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**transcribed_text** | **string** | Transcribed text | [default to undefined]
**response_text** | **string** | AI response text | [default to undefined]
**audio_url** | **string** |  | [optional] [default to undefined]
**emotion_detected** | **string** |  | [optional] [default to undefined]
**facts_extracted** | **number** | Number of facts extracted | [optional] [default to 0]
**processing_time_ms** | **number** | Total processing time | [default to undefined]

## Example

```typescript
import { VoiceProcessingResponse } from 'privet-api-client';

const instance: VoiceProcessingResponse = {
    transcribed_text,
    response_text,
    audio_url,
    emotion_detected,
    facts_extracted,
    processing_time_ms,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
