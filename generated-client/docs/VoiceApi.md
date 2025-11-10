# VoiceApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getAudioFileApiV1VoiceAudioAudioIdGet**](#getaudiofileapiv1voiceaudioaudioidget) | **GET** /api/v1/voice/audio/{audio_id} | Get Audio File|
|[**getTtsProvidersApiV1VoiceProvidersGet**](#getttsprovidersapiv1voiceprovidersget) | **GET** /api/v1/voice/providers | Get Tts Providers|
|[**processVoiceMessageApiV1VoiceProcessPost**](#processvoicemessageapiv1voiceprocesspost) | **POST** /api/v1/voice/process | Process Voice Message|
|[**synthesizeSpeechApiV1VoiceSynthesizePost**](#synthesizespeechapiv1voicesynthesizepost) | **POST** /api/v1/voice/synthesize | Synthesize Speech|
|[**transcribeAudioApiV1VoiceTranscribePost**](#transcribeaudioapiv1voicetranscribepost) | **POST** /api/v1/voice/transcribe | Transcribe Audio|

# **getAudioFileApiV1VoiceAudioAudioIdGet**
> any getAudioFileApiV1VoiceAudioAudioIdGet()

Download a generated audio file.

### Example

```typescript
import {
    VoiceApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new VoiceApi(configuration);

let audioId: string; // (default to undefined)

const { status, data } = await apiInstance.getAudioFileApiV1VoiceAudioAudioIdGet(
    audioId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **audioId** | [**string**] |  | defaults to undefined|


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTtsProvidersApiV1VoiceProvidersGet**
> Array<TTSProvider> getTtsProvidersApiV1VoiceProvidersGet()

Get available TTS providers and their capabilities.

### Example

```typescript
import {
    VoiceApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new VoiceApi(configuration);

const { status, data } = await apiInstance.getTtsProvidersApiV1VoiceProvidersGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<TTSProvider>**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **processVoiceMessageApiV1VoiceProcessPost**
> VoiceProcessingResponse processVoiceMessageApiV1VoiceProcessPost()

Complete voice processing pipeline: STT -> AI -> TTS.

### Example

```typescript
import {
    VoiceApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new VoiceApi(configuration);

let audioFile: File; // (default to undefined)
let userId: number; // (default to undefined)
let language: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.processVoiceMessageApiV1VoiceProcessPost(
    audioFile,
    userId,
    language
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **audioFile** | [**File**] |  | defaults to undefined|
| **userId** | [**number**] |  | defaults to undefined|
| **language** | [**string**] |  | (optional) defaults to undefined|


### Return type

**VoiceProcessingResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **synthesizeSpeechApiV1VoiceSynthesizePost**
> SynthesisResponse synthesizeSpeechApiV1VoiceSynthesizePost(synthesisRequest)

Synthesize text to speech using TTS.

### Example

```typescript
import {
    VoiceApi,
    Configuration,
    SynthesisRequest
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new VoiceApi(configuration);

let synthesisRequest: SynthesisRequest; //

const { status, data } = await apiInstance.synthesizeSpeechApiV1VoiceSynthesizePost(
    synthesisRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **synthesisRequest** | **SynthesisRequest**|  | |


### Return type

**SynthesisResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **transcribeAudioApiV1VoiceTranscribePost**
> TranscriptionResponse transcribeAudioApiV1VoiceTranscribePost()

Transcribe audio to text using STT.

### Example

```typescript
import {
    VoiceApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new VoiceApi(configuration);

let audioFile: File; // (default to undefined)
let userId: number; // (optional) (default to undefined)
let language: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.transcribeAudioApiV1VoiceTranscribePost(
    audioFile,
    userId,
    language
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **audioFile** | [**File**] |  | defaults to undefined|
| **userId** | [**number**] |  | (optional) defaults to undefined|
| **language** | [**string**] |  | (optional) defaults to undefined|


### Return type

**TranscriptionResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

