# MemoryContext

Complete memory context for a user.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**relevant_facts** | [**Array&lt;FactSearchResult&gt;**](FactSearchResult.md) | Relevant facts | [default to undefined]
**profile_summaries** | [**Array&lt;ProfileSummary&gt;**](ProfileSummary.md) | Profile summaries | [default to undefined]
**recent_messages** | **Array&lt;{ [key: string]: any; }&gt;** | Recent conversation messages | [default to undefined]
**context_timestamp** | **string** | Context generation timestamp | [default to undefined]

## Example

```typescript
import { MemoryContext } from 'privet-api-client';

const instance: MemoryContext = {
    user_id,
    relevant_facts,
    profile_summaries,
    recent_messages,
    context_timestamp,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
