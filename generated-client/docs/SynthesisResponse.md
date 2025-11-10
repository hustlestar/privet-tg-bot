# SynthesisResponse

Response from text-to-speech synthesis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**audio_url** | **string** |  | [optional] [default to undefined]
**audio_base64** | **string** |  | [optional] [default to undefined]
**duration_seconds** | **number** |  | [optional] [default to undefined]
**provider** | **string** | TTS provider used | [default to undefined]
**voice** | **string** | Voice used | [default to undefined]

## Example

```typescript
import { SynthesisResponse } from 'privet-api-client';

const instance: SynthesisResponse = {
    audio_url,
    audio_base64,
    duration_seconds,
    provider,
    voice,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
