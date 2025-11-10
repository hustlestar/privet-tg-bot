# TTSProvider

TTS provider information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Provider name | [default to undefined]
**voices** | **Array&lt;{ [key: string]: string; }&gt;** | Available voices | [default to undefined]
**languages** | **Array&lt;string&gt;** | Supported languages | [default to undefined]
**features** | **{ [key: string]: any; }** | Provider features | [default to undefined]

## Example

```typescript
import { TTSProvider } from 'privet-api-client';

const instance: TTSProvider = {
    name,
    voices,
    languages,
    features,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
