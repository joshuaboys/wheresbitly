# Upload Image to Azure Function

## Intro

This project shows how to implement a httptrigger using Azure Functions V2 which can receive and image and persist it to blob storage.

## Prerequisites

- [Azure Function Core Tools](https://github.com/Azure/azure-functions-core-tools) (V2)

## Usage

### Create Blob Storage Account

1. Create Blob Storage Account in the Azure Portal. Go to Keys and note the connection string, you'll need this later.

### Run Function App

1. Clone repository
2. Add local.settings.json to the project and provide these values:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureStorageConnectionString": "Endpoint=INSERT_YOUR_SIGNALRSERVICE_ENDPOINT_HERE;"
  },
  "Host": {
    "LocalHttpPort": 7081,
    "CORS": "*"
  }
}
```

3. Start Debugging

### Run Angular Client App

1. Clone repository
2. Run npm install to install required dependencies
3. Run ng serve to start local test server
4. Open http://localhost:4200 in (multiple) browser windows
5. Upload and image message and send