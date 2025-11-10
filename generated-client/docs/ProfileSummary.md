# ProfileSummary

User profile summary schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]
**id** | **number** | Summary ID | [default to undefined]
**user_id** | **number** | User ID | [default to undefined]
**summary_text** | **string** | Summary text | [default to undefined]
**summary_topic** | **string** | Summary topic | [default to undefined]
**last_updated** | **string** | Last update timestamp | [default to undefined]

## Example

```typescript
import { ProfileSummary } from 'privet-api-client';

const instance: ProfileSummary = {
    created_at,
    updated_at,
    id,
    user_id,
    summary_text,
    summary_topic,
    last_updated,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
