# User

Complete user schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** |  | [optional] [default to undefined]
**username** | **string** |  | [optional] [default to undefined]
**first_name** | **string** |  | [optional] [default to undefined]
**last_name** | **string** |  | [optional] [default to undefined]
**language** | **string** | User language code | [optional] [default to 'en']
**user_id** | **number** | User ID | [default to undefined]
**is_active** | **boolean** | User active status | [optional] [default to true]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { User } from 'privet-api-client';

const instance: User = {
    created_at,
    updated_at,
    username,
    first_name,
    last_name,
    language,
    user_id,
    is_active,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
