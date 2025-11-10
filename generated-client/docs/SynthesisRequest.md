# SynthesisRequest

Request for text-to-speech synthesis.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **string** | Text to synthesize | [default to undefined]
**voice** | **string** |  | [optional] [default to undefined]
**emotion** | **string** |  | [optional] [default to undefined]
**speed** | **number** | Speech speed | [optional] [default to 1.0]
**language** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { SynthesisRequest } from 'privet-api-client';

const instance: SynthesisRequest = {
    text,
    voice,
    emotion,
    speed,
    language,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
