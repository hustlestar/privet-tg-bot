# ConversationResponse

Response from conversation processing.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**response_text** | **string** | AI response text | [default to undefined]
**emotion** | [**EmotionType**](EmotionType.md) |  | [optional] [default to undefined]
**facts_extracted** | **number** | Number of facts extracted | [optional] [default to 0]
**context_used** | **boolean** | Whether context was used | [optional] [default to false]
**processing_time_ms** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { ConversationResponse } from 'privet-api-client';

const instance: ConversationResponse = {
    response_text,
    emotion,
    facts_extracted,
    context_used,
    processing_time_ms,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
