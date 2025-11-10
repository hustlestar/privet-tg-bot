# PaginatedResponse

Paginated response schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | **Array&lt;any&gt;** | List of items | [default to undefined]
**total** | **number** | Total number of items | [default to undefined]
**offset** | **number** | Current offset | [default to undefined]
**limit** | **number** | Current limit | [default to undefined]

## Example

```typescript
import { PaginatedResponse } from 'privet-api-client';

const instance: PaginatedResponse = {
    items,
    total,
    offset,
    limit,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
