# MemoryApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createFactApiV1MemoryFactsPost**](#createfactapiv1memoryfactspost) | **POST** /api/v1/memory/facts | Create Fact|
|[**deleteFactApiV1MemoryFactsFactIdDelete**](#deletefactapiv1memoryfactsfactiddelete) | **DELETE** /api/v1/memory/facts/{fact_id} | Delete Fact|
|[**generateProfileSummaryApiV1MemorySummariesGeneratePost**](#generateprofilesummaryapiv1memorysummariesgeneratepost) | **POST** /api/v1/memory/summaries/generate | Generate Profile Summary|
|[**getMemoryContextApiV1MemoryContextUserIdGet**](#getmemorycontextapiv1memorycontextuseridget) | **GET** /api/v1/memory/context/{user_id} | Get Memory Context|
|[**getMemoryStatsApiV1MemoryStatsUserIdGet**](#getmemorystatsapiv1memorystatsuseridget) | **GET** /api/v1/memory/stats/{user_id} | Get Memory Stats|
|[**getProfileSummariesApiV1MemorySummariesUserIdGet**](#getprofilesummariesapiv1memorysummariesuseridget) | **GET** /api/v1/memory/summaries/{user_id} | Get Profile Summaries|
|[**getUserFactsApiV1MemoryFactsUserIdGet**](#getuserfactsapiv1memoryfactsuseridget) | **GET** /api/v1/memory/facts/{user_id} | Get User Facts|
|[**searchFactsApiV1MemoryFactsSearchPost**](#searchfactsapiv1memoryfactssearchpost) | **POST** /api/v1/memory/facts/search | Search Facts|

# **createFactApiV1MemoryFactsPost**
> UserFact createFactApiV1MemoryFactsPost(factCreate)

Store a new fact for a user.

### Example

```typescript
import {
    MemoryApi,
    Configuration,
    FactCreate
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let factCreate: FactCreate; //

const { status, data } = await apiInstance.createFactApiV1MemoryFactsPost(
    factCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **factCreate** | **FactCreate**|  | |


### Return type

**UserFact**

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

# **deleteFactApiV1MemoryFactsFactIdDelete**
> { [key: string]: any; } deleteFactApiV1MemoryFactsFactIdDelete()

Delete a specific fact.

### Example

```typescript
import {
    MemoryApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let factId: number; // (default to undefined)

const { status, data } = await apiInstance.deleteFactApiV1MemoryFactsFactIdDelete(
    factId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **factId** | [**number**] |  | defaults to undefined|


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

# **generateProfileSummaryApiV1MemorySummariesGeneratePost**
> ProfileSummary generateProfileSummaryApiV1MemorySummariesGeneratePost(profileSummaryCreate)

Generate or update user profile summary.

### Example

```typescript
import {
    MemoryApi,
    Configuration,
    ProfileSummaryCreate
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let profileSummaryCreate: ProfileSummaryCreate; //

const { status, data } = await apiInstance.generateProfileSummaryApiV1MemorySummariesGeneratePost(
    profileSummaryCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileSummaryCreate** | **ProfileSummaryCreate**|  | |


### Return type

**ProfileSummary**

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

# **getMemoryContextApiV1MemoryContextUserIdGet**
> MemoryContext getMemoryContextApiV1MemoryContextUserIdGet()

Get complete memory context for a user.

### Example

```typescript
import {
    MemoryApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let userId: number; // (default to undefined)
let query: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getMemoryContextApiV1MemoryContextUserIdGet(
    userId,
    query
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|
| **query** | [**string**] |  | (optional) defaults to undefined|


### Return type

**MemoryContext**

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

# **getMemoryStatsApiV1MemoryStatsUserIdGet**
> MemoryStats getMemoryStatsApiV1MemoryStatsUserIdGet()

Get memory statistics for a user.

### Example

```typescript
import {
    MemoryApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let userId: number; // (default to undefined)

const { status, data } = await apiInstance.getMemoryStatsApiV1MemoryStatsUserIdGet(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|


### Return type

**MemoryStats**

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

# **getProfileSummariesApiV1MemorySummariesUserIdGet**
> Array<ProfileSummary> getProfileSummariesApiV1MemorySummariesUserIdGet()

Get all profile summaries for a user.

### Example

```typescript
import {
    MemoryApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let userId: number; // (default to undefined)

const { status, data } = await apiInstance.getProfileSummariesApiV1MemorySummariesUserIdGet(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|


### Return type

**Array<ProfileSummary>**

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

# **getUserFactsApiV1MemoryFactsUserIdGet**
> Array<UserFact> getUserFactsApiV1MemoryFactsUserIdGet()

Get all facts for a user.

### Example

```typescript
import {
    MemoryApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let userId: number; // (default to undefined)
let limit: number; // (optional) (default to 20)
let offset: number; // (optional) (default to 0)
let category: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getUserFactsApiV1MemoryFactsUserIdGet(
    userId,
    limit,
    offset,
    category
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 20|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **category** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<UserFact>**

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

# **searchFactsApiV1MemoryFactsSearchPost**
> Array<FactSearchResult> searchFactsApiV1MemoryFactsSearchPost(factSearch)

Search for relevant facts using semantic similarity.

### Example

```typescript
import {
    MemoryApi,
    Configuration,
    FactSearch
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new MemoryApi(configuration);

let factSearch: FactSearch; //

const { status, data } = await apiInstance.searchFactsApiV1MemoryFactsSearchPost(
    factSearch
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **factSearch** | **FactSearch**|  | |


### Return type

**Array<FactSearchResult>**

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

