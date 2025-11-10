# FactSearch

Schema for searching facts.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**query** | **string** | Search query | [default to undefined]
**limit** | **number** | Maximum results | [optional] [default to 5]
**min_similarity** | **number** | Minimum similarity score | [optional] [default to 0.7]

## Example

```typescript
import { FactSearch } from 'privet-api-client';

const instance: FactSearch = {
    user_id,
    query,
    limit,
    min_similarity,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
