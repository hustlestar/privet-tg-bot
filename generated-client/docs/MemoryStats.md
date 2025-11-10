# MemoryStats

Memory statistics for a user.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**total_facts** | **number** | Total facts stored | [default to undefined]
**fact_categories** | **{ [key: string]: number; }** | Facts by category | [default to undefined]
**profile_summaries_count** | **number** | Number of profile summaries | [default to undefined]
**memory_density** | **number** | Memory density score | [default to undefined]
**last_fact_date** | **string** |  | [optional] [default to undefined]
**storage_size_bytes** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { MemoryStats } from 'privet-api-client';

const instance: MemoryStats = {
    user_id,
    total_facts,
    fact_categories,
    profile_summaries_count,
    memory_density,
    last_fact_date,
    storage_size_bytes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
