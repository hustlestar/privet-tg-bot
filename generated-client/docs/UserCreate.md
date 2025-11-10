# UserCreate

Schema for creating a user.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **string** |  | [optional] [default to undefined]
**first_name** | **string** |  | [optional] [default to undefined]
**last_name** | **string** |  | [optional] [default to undefined]
**language** | **string** | User language code | [optional] [default to 'en']
**user_id** | **number** | Telegram user ID | [default to undefined]

## Example

```typescript
import { UserCreate } from 'privet-api-client';

const instance: UserCreate = {
    username,
    first_name,
    last_name,
    language,
    user_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
