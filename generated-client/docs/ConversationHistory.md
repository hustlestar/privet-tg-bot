# ConversationHistory

Conversation history schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**messages** | [**Array&lt;ConversationMessage&gt;**](ConversationMessage.md) | List of messages | [default to undefined]
**total_messages** | **number** | Total message count | [default to undefined]
**date_range** | **{ [key: string]: string; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ConversationHistory } from 'privet-api-client';

const instance: ConversationHistory = {
    user_id,
    messages,
    total_messages,
    date_range,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
