# UsersApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createUserApiV1UsersPost**](#createuserapiv1userspost) | **POST** /api/v1/users/ | Create User|
|[**deleteUserApiV1UsersUserIdDelete**](#deleteuserapiv1usersuseriddelete) | **DELETE** /api/v1/users/{user_id} | Delete User|
|[**getUserApiV1UsersUserIdGet**](#getuserapiv1usersuseridget) | **GET** /api/v1/users/{user_id} | Get User|
|[**getUserStatsApiV1UsersUserIdStatsGet**](#getuserstatsapiv1usersuseridstatsget) | **GET** /api/v1/users/{user_id}/stats | Get User Stats|
|[**listUsersApiV1UsersGet**](#listusersapiv1usersget) | **GET** /api/v1/users/ | List Users|
|[**updateUserApiV1UsersUserIdPut**](#updateuserapiv1usersuseridput) | **PUT** /api/v1/users/{user_id} | Update User|

# **createUserApiV1UsersPost**
> User createUserApiV1UsersPost(userCreate)

Create a new user.

### Example

```typescript
import {
    UsersApi,
    Configuration,
    UserCreate
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userCreate: UserCreate; //

const { status, data } = await apiInstance.createUserApiV1UsersPost(
    userCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userCreate** | **UserCreate**|  | |


### Return type

**User**

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

# **deleteUserApiV1UsersUserIdDelete**
> { [key: string]: any; } deleteUserApiV1UsersUserIdDelete()

Delete a user and all associated data.

### Example

```typescript
import {
    UsersApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: number; // (default to undefined)

const { status, data } = await apiInstance.deleteUserApiV1UsersUserIdDelete(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|


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

# **getUserApiV1UsersUserIdGet**
> User getUserApiV1UsersUserIdGet()

Get user by ID.

### Example

```typescript
import {
    UsersApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: number; // (default to undefined)

const { status, data } = await apiInstance.getUserApiV1UsersUserIdGet(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|


### Return type

**User**

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

# **getUserStatsApiV1UsersUserIdStatsGet**
> UserStats getUserStatsApiV1UsersUserIdStatsGet()

Get user statistics.

### Example

```typescript
import {
    UsersApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: number; // (default to undefined)

const { status, data } = await apiInstance.getUserStatsApiV1UsersUserIdStatsGet(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**number**] |  | defaults to undefined|


### Return type

**UserStats**

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

# **listUsersApiV1UsersGet**
> PaginatedResponse listUsersApiV1UsersGet()

List all users with pagination.

### Example

```typescript
import {
    UsersApi,
    Configuration
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let offset: number; // (optional) (default to 0)
let limit: number; // (optional) (default to 20)

const { status, data } = await apiInstance.listUsersApiV1UsersGet(
    offset,
    limit
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **limit** | [**number**] |  | (optional) defaults to 20|


### Return type

**PaginatedResponse**

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

# **updateUserApiV1UsersUserIdPut**
> User updateUserApiV1UsersUserIdPut(userUpdate)

Update user information.

### Example

```typescript
import {
    UsersApi,
    Configuration,
    UserUpdate
} from 'privet-api-client';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: number; // (default to undefined)
let userUpdate: UserUpdate; //

const { status, data } = await apiInstance.updateUserApiV1UsersUserIdPut(
    userId,
    userUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userUpdate** | **UserUpdate**|  | |
| **userId** | [**number**] |  | defaults to undefined|


### Return type

**User**

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

