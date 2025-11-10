# ConversationsApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**analyzeEmotionApiV1ConversationsUserIdAnalyzeEmotionPost**](#analyzeemotionapiv1conversationsuseridanalyzeemotionpost) | **POST** /api/v1/conversations/{user_id}/analyze-emotion | Analyze Emotion|
|[**deleteMessageApiV1ConversationsUserIdMessagesMessageIdDelete**](#deletemessageapiv1conversationsuseridmessagesmessageiddelete) | **DELETE** /api/v1/conversations/{user_id}/messages/{message_id} | Delete Message|
|[**getConversationHistoryApiV1ConversationsUserIdHistoryGet**](#getconversationhistoryapiv1conversationsuseridhistoryget) | **GET** /api/v1/conversations/{user_id}/history | Get Conversation History|
|[**processConversationApiV1ConversationsProcessPost**](#processconversationapiv1conversationsprocesspost) | **POST** /api/v1/conversations/process | Process Conversation|

# **analyzeEmotionApiV1ConversationsUserIdAnalyzeEmotionPost**
> EmotionAnalysis analyzeEmotionApiV1ConversationsUserIdAnalyzeEmotionPost()

Analyze emotion in text.

### Example

```typescript
import {
    ConversationsApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ConversationsApi(configuration);

let userId: number; // (default to undefined)
let text: string; // (default to undefined)

const { status, data } = await apiInstance.analyzeEmotionApiV1ConversationsUserIdAnalyzeEmotionPost(
    userId,
    text
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|
| **text** | [**string**] |  | defaults to undefined|


### Return type

**EmotionAnalysis**

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

# **deleteMessageApiV1ConversationsUserIdMessagesMessageIdDelete**
> { [key: string]: any; } deleteMessageApiV1ConversationsUserIdMessagesMessageIdDelete()

Delete a specific conversation message.

### Example

```typescript
import {
    ConversationsApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ConversationsApi(configuration);

let userId: number; // (default to undefined)
let messageId: number; // (default to undefined)

const { status, data } = await apiInstance.deleteMessageApiV1ConversationsUserIdMessagesMessageIdDelete(
    userId,
    messageId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|
| **messageId** | [**number**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

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

# **getConversationHistoryApiV1ConversationsUserIdHistoryGet**
> ConversationHistory getConversationHistoryApiV1ConversationsUserIdHistoryGet()

Get conversation history for a user.

### Example

```typescript
import {
    ConversationsApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ConversationsApi(configuration);

let userId: number; // (default to undefined)
let limit: number; // (optional) (default to 20)
let offset: number; // (optional) (default to 0)

const { status, data } = await apiInstance.getConversationHistoryApiV1ConversationsUserIdHistoryGet(
    userId,
    limit,
    offset
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 20|
| **offset** | [**number**] |  | (optional) defaults to 0|


### Return type

**ConversationHistory**

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

# **processConversationApiV1ConversationsProcessPost**
> ConversationResponse processConversationApiV1ConversationsProcessPost(conversationRequest)

Process a conversation message and generate a response.

### Example

```typescript
import {
    ConversationsApi,
    Configuration,
    ConversationRequest
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ConversationsApi(configuration);

let conversationRequest: ConversationRequest; //

const { status, data } = await apiInstance.processConversationApiV1ConversationsProcessPost(
    conversationRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationRequest** | **ConversationRequest**|  | |


### Return type

**ConversationResponse**

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

