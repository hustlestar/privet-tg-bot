# ConversationRequest

Request to process a conversation message.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**message** | **string** | Message text | [default to undefined]
**is_voice** | **boolean** | Whether this is from voice | [optional] [default to false]
**context** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ConversationRequest } from 'privet-api-client';

const instance: ConversationRequest = {
    user_id,
    message,
    is_voice,
    context,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
