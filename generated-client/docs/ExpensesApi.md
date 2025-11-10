# ExpensesApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getCostBreakdownApiV1ExpensesCostBreakdownGet**](#getcostbreakdownapiv1expensescostbreakdownget) | **GET** /api/v1/expenses/cost-breakdown | Get Cost Breakdown|
|[**getModelUsageApiV1ExpensesModelsGet**](#getmodelusageapiv1expensesmodelsget) | **GET** /api/v1/expenses/models | Get Model Usage|
|[**getRecentUsageApiV1ExpensesRecentUsageGet**](#getrecentusageapiv1expensesrecentusageget) | **GET** /api/v1/expenses/recent-usage | Get Recent Usage|
|[**getTotalCostsApiV1ExpensesTotalCostsGet**](#gettotalcostsapiv1expensestotalcostsget) | **GET** /api/v1/expenses/total-costs | Get Total Costs|
|[**getUsageStatsApiV1ExpensesUsageStatsGet**](#getusagestatsapiv1expensesusagestatsget) | **GET** /api/v1/expenses/usage-stats | Get Usage Stats|

# **getCostBreakdownApiV1ExpensesCostBreakdownGet**
> { [key: string]: any; } getCostBreakdownApiV1ExpensesCostBreakdownGet()

Get cost breakdown by service, provider, and model.

### Example

```typescript
import {
    ExpensesApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ExpensesApi(configuration);

let userId: number; //Filter by user ID (optional) (default to undefined)
let days: number; //Number of days to analyze (optional) (default to 30)

const { status, data } = await apiInstance.getCostBreakdownApiV1ExpensesCostBreakdownGet(
    userId,
    days
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] | Filter by user ID | (optional) defaults to undefined|
| **days** | [**number**] | Number of days to analyze | (optional) defaults to 30|


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

# **getModelUsageApiV1ExpensesModelsGet**
> { [key: string]: any; } getModelUsageApiV1ExpensesModelsGet()

Get usage breakdown by model.

### Example

```typescript
import {
    ExpensesApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ExpensesApi(configuration);

let days: number; //Number of days to analyze (optional) (default to 30)

const { status, data } = await apiInstance.getModelUsageApiV1ExpensesModelsGet(
    days
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **days** | [**number**] | Number of days to analyze | (optional) defaults to 30|


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

# **getRecentUsageApiV1ExpensesRecentUsageGet**
> { [key: string]: any; } getRecentUsageApiV1ExpensesRecentUsageGet()

Get recent API usage records.

### Example

```typescript
import {
    ExpensesApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ExpensesApi(configuration);

let userId: number; //Filter by user ID (optional) (default to undefined)
let limit: number; //Number of records to return (optional) (default to 50)

const { status, data } = await apiInstance.getRecentUsageApiV1ExpensesRecentUsageGet(
    userId,
    limit
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] | Filter by user ID | (optional) defaults to undefined|
| **limit** | [**number**] | Number of records to return | (optional) defaults to 50|


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

# **getTotalCostsApiV1ExpensesTotalCostsGet**
> { [key: string]: any; } getTotalCostsApiV1ExpensesTotalCostsGet()

Get total costs and usage statistics.

### Example

```typescript
import {
    ExpensesApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ExpensesApi(configuration);

let userId: number; //Filter by user ID (optional) (default to undefined)
let days: number; //Number of days to analyze (optional) (default to 30)

const { status, data } = await apiInstance.getTotalCostsApiV1ExpensesTotalCostsGet(
    userId,
    days
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] | Filter by user ID | (optional) defaults to undefined|
| **days** | [**number**] | Number of days to analyze | (optional) defaults to 30|


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

# **getUsageStatsApiV1ExpensesUsageStatsGet**
> { [key: string]: any; } getUsageStatsApiV1ExpensesUsageStatsGet()

Get detailed usage statistics.

### Example

```typescript
import {
    ExpensesApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new ExpensesApi(configuration);

let userId: number; //Filter by user ID (optional) (default to undefined)
let serviceType: string; //Filter by service type (optional) (default to undefined)
let provider: string; //Filter by provider (optional) (default to undefined)
let days: number; //Number of days to analyze (optional) (default to 30)

const { status, data } = await apiInstance.getUsageStatsApiV1ExpensesUsageStatsGet(
    userId,
    serviceType,
    provider,
    days
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] | Filter by user ID | (optional) defaults to undefined|
| **serviceType** | [**string**] | Filter by service type | (optional) defaults to undefined|
| **provider** | [**string**] | Filter by provider | (optional) defaults to undefined|
| **days** | [**number**] | Number of days to analyze | (optional) defaults to 30|


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

