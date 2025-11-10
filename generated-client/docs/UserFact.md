# UserFact

User fact schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]
**id** | **number** | Fact ID | [default to undefined]
**user_id** | **number** | User ID | [default to undefined]
**fact_text** | **string** | Fact text | [default to undefined]
**fact_summary** | **string** |  | [optional] [default to undefined]
**source_message_id** | **number** |  | [optional] [default to undefined]
**confidence** | **number** | Fact confidence | [optional] [default to 1.0]
**category** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { UserFact } from 'privet-api-client';

const instance: UserFact = {
    created_at,
    updated_at,
    id,
    user_id,
    fact_text,
    fact_summary,
    source_message_id,
    confidence,
    category,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
