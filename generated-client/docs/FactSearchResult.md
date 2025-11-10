# FactSearchResult

Fact search result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fact** | [**UserFact**](UserFact.md) | The fact | [default to undefined]
**similarity** | **number** | Similarity score | [default to undefined]
**relevance_reason** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { FactSearchResult } from 'privet-api-client';

const instance: FactSearchResult = {
    fact,
    similarity,
    relevance_reason,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
