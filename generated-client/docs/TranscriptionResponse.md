# TranscriptionResponse

Response from voice transcription.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **string** | Transcribed text | [default to undefined]
**language** | **string** |  | [optional] [default to undefined]
**confidence** | **number** |  | [optional] [default to undefined]
**duration_seconds** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { TranscriptionResponse } from 'privet-api-client';

const instance: TranscriptionResponse = {
    text,
    language,
    confidence,
    duration_seconds,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
