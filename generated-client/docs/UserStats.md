# UserStats

User statistics schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**total_messages** | **number** | Total messages sent | [optional] [default to 0]
**total_voice_messages** | **number** | Total voice messages | [optional] [default to 0]
**total_facts** | **number** | Total facts stored | [optional] [default to 0]
**profile_summaries** | **number** | Number of profile summaries | [optional] [default to 0]
**memory_density** | **number** | Memory density score | [optional] [default to 0.0]
**last_active** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { UserStats } from 'privet-api-client';

const instance: UserStats = {
    user_id,
    total_messages,
    total_voice_messages,
    total_facts,
    profile_summaries,
    memory_density,
    last_active,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
