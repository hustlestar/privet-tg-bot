# UserUpdate

Schema for updating a user.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **string** |  | [optional] [default to undefined]
**first_name** | **string** |  | [optional] [default to undefined]
**last_name** | **string** |  | [optional] [default to undefined]
**language** | **string** | User language code | [optional] [default to 'en']

## Example

```typescript
import { UserUpdate } from 'privet-api-client';

const instance: UserUpdate = {
    username,
    first_name,
    last_name,
    language,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
