# ConversationMessage

Conversation message schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]
**id** | **number** | Message ID | [default to undefined]
**user_id** | **number** | User ID | [default to undefined]
**role** | [**MessageRole**](MessageRole.md) | Message role | [default to undefined]
**message_text** | **string** |  | [optional] [default to undefined]
**transcribed_text** | **string** |  | [optional] [default to undefined]
**sentiment_score** | **number** |  | [optional] [default to undefined]
**emotion** | [**EmotionType**](EmotionType.md) |  | [optional] [default to undefined]
**is_voice** | **boolean** | Whether this was a voice message | [optional] [default to false]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ConversationMessage } from 'privet-api-client';

const instance: ConversationMessage = {
    created_at,
    updated_at,
    id,
    user_id,
    role,
    message_text,
    transcribed_text,
    sentiment_score,
    emotion,
    is_voice,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
