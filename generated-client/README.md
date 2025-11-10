## privet-api-client@1.0.0

This generator creates TypeScript/JavaScript client that utilizes [axios](https://github.com/axios/axios). The generated Node module can be used in the following environments:

Environment
* Node.js
* Webpack
* Browserify

Language level
* ES5 - you must have a Promises/A+ library installed
* ES6

Module system
* CommonJS
* ES6 module system

It can be used in both TypeScript and JavaScript. In TypeScript, the definition will be automatically resolved via `package.json`. ([Reference](https://www.typescriptlang.org/docs/handbook/declaration-files/consumption.html))

### Building

To build and compile the typescript sources to javascript use:
```
npm install
npm run build
```

### Publishing

First build the package then run `npm publish`

### Consuming

navigate to the folder of your consuming project and run one of the following commands.

_published:_

```
npm install privet-api-client@1.0.0 --save
```

_unPublished (not recommended):_

```
npm install PATH_TO_GENERATED_PACKAGE --save
```

### Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ConversationsApi* | [**analyzeEmotionApiV1ConversationsUserIdAnalyzeEmotionPost**](docs/ConversationsApi.md#analyzeemotionapiv1conversationsuseridanalyzeemotionpost) | **POST** /api/v1/conversations/{user_id}/analyze-emotion | Analyze Emotion
*ConversationsApi* | [**deleteMessageApiV1ConversationsUserIdMessagesMessageIdDelete**](docs/ConversationsApi.md#deletemessageapiv1conversationsuseridmessagesmessageiddelete) | **DELETE** /api/v1/conversations/{user_id}/messages/{message_id} | Delete Message
*ConversationsApi* | [**getConversationHistoryApiV1ConversationsUserIdHistoryGet**](docs/ConversationsApi.md#getconversationhistoryapiv1conversationsuseridhistoryget) | **GET** /api/v1/conversations/{user_id}/history | Get Conversation History
*ConversationsApi* | [**processConversationApiV1ConversationsProcessPost**](docs/ConversationsApi.md#processconversationapiv1conversationsprocesspost) | **POST** /api/v1/conversations/process | Process Conversation
*DefaultApi* | [**healthCheckHealthGet**](docs/DefaultApi.md#healthcheckhealthget) | **GET** /health | Health Check
*ExpensesApi* | [**getCostBreakdownApiV1ExpensesCostBreakdownGet**](docs/ExpensesApi.md#getcostbreakdownapiv1expensescostbreakdownget) | **GET** /api/v1/expenses/cost-breakdown | Get Cost Breakdown
*ExpensesApi* | [**getModelUsageApiV1ExpensesModelsGet**](docs/ExpensesApi.md#getmodelusageapiv1expensesmodelsget) | **GET** /api/v1/expenses/models | Get Model Usage
*ExpensesApi* | [**getRecentUsageApiV1ExpensesRecentUsageGet**](docs/ExpensesApi.md#getrecentusageapiv1expensesrecentusageget) | **GET** /api/v1/expenses/recent-usage | Get Recent Usage
*ExpensesApi* | [**getTotalCostsApiV1ExpensesTotalCostsGet**](docs/ExpensesApi.md#gettotalcostsapiv1expensestotalcostsget) | **GET** /api/v1/expenses/total-costs | Get Total Costs
*ExpensesApi* | [**getUsageStatsApiV1ExpensesUsageStatsGet**](docs/ExpensesApi.md#getusagestatsapiv1expensesusagestatsget) | **GET** /api/v1/expenses/usage-stats | Get Usage Stats
*HealthApi* | [**healthStatusApiV1HealthStatusGet**](docs/HealthApi.md#healthstatusapiv1healthstatusget) | **GET** /api/v1/health/status | Health Status
*HealthApi* | [**livenessCheckApiV1HealthLiveGet**](docs/HealthApi.md#livenesscheckapiv1healthliveget) | **GET** /api/v1/health/live | Liveness Check
*HealthApi* | [**readinessCheckApiV1HealthReadyGet**](docs/HealthApi.md#readinesscheckapiv1healthreadyget) | **GET** /api/v1/health/ready | Readiness Check
*MemoryApi* | [**createFactApiV1MemoryFactsPost**](docs/MemoryApi.md#createfactapiv1memoryfactspost) | **POST** /api/v1/memory/facts | Create Fact
*MemoryApi* | [**deleteFactApiV1MemoryFactsFactIdDelete**](docs/MemoryApi.md#deletefactapiv1memoryfactsfactiddelete) | **DELETE** /api/v1/memory/facts/{fact_id} | Delete Fact
*MemoryApi* | [**generateProfileSummaryApiV1MemorySummariesGeneratePost**](docs/MemoryApi.md#generateprofilesummaryapiv1memorysummariesgeneratepost) | **POST** /api/v1/memory/summaries/generate | Generate Profile Summary
*MemoryApi* | [**getMemoryContextApiV1MemoryContextUserIdGet**](docs/MemoryApi.md#getmemorycontextapiv1memorycontextuseridget) | **GET** /api/v1/memory/context/{user_id} | Get Memory Context
*MemoryApi* | [**getMemoryStatsApiV1MemoryStatsUserIdGet**](docs/MemoryApi.md#getmemorystatsapiv1memorystatsuseridget) | **GET** /api/v1/memory/stats/{user_id} | Get Memory Stats
*MemoryApi* | [**getProfileSummariesApiV1MemorySummariesUserIdGet**](docs/MemoryApi.md#getprofilesummariesapiv1memorysummariesuseridget) | **GET** /api/v1/memory/summaries/{user_id} | Get Profile Summaries
*MemoryApi* | [**getUserFactsApiV1MemoryFactsUserIdGet**](docs/MemoryApi.md#getuserfactsapiv1memoryfactsuseridget) | **GET** /api/v1/memory/facts/{user_id} | Get User Facts
*MemoryApi* | [**searchFactsApiV1MemoryFactsSearchPost**](docs/MemoryApi.md#searchfactsapiv1memoryfactssearchpost) | **POST** /api/v1/memory/facts/search | Search Facts
*UsersApi* | [**createUserApiV1UsersPost**](docs/UsersApi.md#createuserapiv1userspost) | **POST** /api/v1/users/ | Create User
*UsersApi* | [**deleteUserApiV1UsersUserIdDelete**](docs/UsersApi.md#deleteuserapiv1usersuseriddelete) | **DELETE** /api/v1/users/{user_id} | Delete User
*UsersApi* | [**getUserApiV1UsersUserIdGet**](docs/UsersApi.md#getuserapiv1usersuseridget) | **GET** /api/v1/users/{user_id} | Get User
*UsersApi* | [**getUserStatsApiV1UsersUserIdStatsGet**](docs/UsersApi.md#getuserstatsapiv1usersuseridstatsget) | **GET** /api/v1/users/{user_id}/stats | Get User Stats
*UsersApi* | [**listUsersApiV1UsersGet**](docs/UsersApi.md#listusersapiv1usersget) | **GET** /api/v1/users/ | List Users
*UsersApi* | [**updateUserApiV1UsersUserIdPut**](docs/UsersApi.md#updateuserapiv1usersuseridput) | **PUT** /api/v1/users/{user_id} | Update User
*VoiceApi* | [**getAudioFileApiV1VoiceAudioAudioIdGet**](docs/VoiceApi.md#getaudiofileapiv1voiceaudioaudioidget) | **GET** /api/v1/voice/audio/{audio_id} | Get Audio File
*VoiceApi* | [**getTtsProvidersApiV1VoiceProvidersGet**](docs/VoiceApi.md#getttsprovidersapiv1voiceprovidersget) | **GET** /api/v1/voice/providers | Get Tts Providers
*VoiceApi* | [**processVoiceMessageApiV1VoiceProcessPost**](docs/VoiceApi.md#processvoicemessageapiv1voiceprocesspost) | **POST** /api/v1/voice/process | Process Voice Message
*VoiceApi* | [**synthesizeSpeechApiV1VoiceSynthesizePost**](docs/VoiceApi.md#synthesizespeechapiv1voicesynthesizepost) | **POST** /api/v1/voice/synthesize | Synthesize Speech
*VoiceApi* | [**transcribeAudioApiV1VoiceTranscribePost**](docs/VoiceApi.md#transcribeaudioapiv1voicetranscribepost) | **POST** /api/v1/voice/transcribe | Transcribe Audio


### Documentation For Models

 - [ConversationHistory](docs/ConversationHistory.md)
 - [ConversationMessage](docs/ConversationMessage.md)
 - [ConversationRequest](docs/ConversationRequest.md)
 - [ConversationResponse](docs/ConversationResponse.md)
 - [EmotionAnalysis](docs/EmotionAnalysis.md)
 - [EmotionType](docs/EmotionType.md)
 - [FactCreate](docs/FactCreate.md)
 - [FactSearch](docs/FactSearch.md)
 - [FactSearchResult](docs/FactSearchResult.md)
 - [HTTPValidationError](docs/HTTPValidationError.md)
 - [MemoryContext](docs/MemoryContext.md)
 - [MemoryStats](docs/MemoryStats.md)
 - [MessageRole](docs/MessageRole.md)
 - [PaginatedResponse](docs/PaginatedResponse.md)
 - [ProfileSummary](docs/ProfileSummary.md)
 - [ProfileSummaryCreate](docs/ProfileSummaryCreate.md)
 - [SynthesisRequest](docs/SynthesisRequest.md)
 - [SynthesisResponse](docs/SynthesisResponse.md)
 - [TTSProvider](docs/TTSProvider.md)
 - [TranscriptionResponse](docs/TranscriptionResponse.md)
 - [User](docs/User.md)
 - [UserCreate](docs/UserCreate.md)
 - [UserFact](docs/UserFact.md)
 - [UserStats](docs/UserStats.md)
 - [UserUpdate](docs/UserUpdate.md)
 - [ValidationError](docs/ValidationError.md)
 - [ValidationErrorLocInner](docs/ValidationErrorLocInner.md)
 - [VoiceProcessingResponse](docs/VoiceProcessingResponse.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization

Endpoints do not require authorization.

