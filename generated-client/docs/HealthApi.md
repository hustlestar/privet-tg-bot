# HealthApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**healthStatusApiV1HealthStatusGet**](#healthstatusapiv1healthstatusget) | **GET** /api/v1/health/status | Health Status|
|[**livenessCheckApiV1HealthLiveGet**](#livenesscheckapiv1healthliveget) | **GET** /api/v1/health/live | Liveness Check|
|[**readinessCheckApiV1HealthReadyGet**](#readinesscheckapiv1healthreadyget) | **GET** /api/v1/health/ready | Readiness Check|

# **healthStatusApiV1HealthStatusGet**
> { [key: string]: any; } healthStatusApiV1HealthStatusGet()

Get API health status.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthStatusApiV1HealthStatusGet();
```

### Parameters
This endpoint does not have any parameters.


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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **livenessCheckApiV1HealthLiveGet**
> { [key: string]: string; } livenessCheckApiV1HealthLiveGet()

Simple liveness check.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.livenessCheckApiV1HealthLiveGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: string; }**

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

# **readinessCheckApiV1HealthReadyGet**
> { [key: string]: any; } readinessCheckApiV1HealthReadyGet()

Check if the API is ready to handle requests.

### Example

```typescript
import {
    HealthApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.readinessCheckApiV1HealthReadyGet();
```

### Parameters
This endpoint does not have any parameters.


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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

