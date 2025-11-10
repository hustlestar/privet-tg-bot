# FactCreate

Schema for creating a fact.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**fact_text** | **string** | Fact text | [default to undefined]
**fact_summary** | **string** |  | [optional] [default to undefined]
**category** | **string** |  | [optional] [default to undefined]
**source_message_id** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { FactCreate } from 'privet-api-client';

const instance: FactCreate = {
    user_id,
    fact_text,
    fact_summary,
    category,
    source_message_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
