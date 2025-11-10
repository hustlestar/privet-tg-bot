# ProfileSummaryCreate

Schema for creating/updating profile summary.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **number** | User ID | [default to undefined]
**summary_topic** | **string** | Summary topic | [optional] [default to 'general']
**force_regenerate** | **boolean** | Force regeneration | [optional] [default to false]

## Example

```typescript
import { ProfileSummaryCreate } from 'privet-api-client';

const instance: ProfileSummaryCreate = {
    user_id,
    summary_topic,
    force_regenerate,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
