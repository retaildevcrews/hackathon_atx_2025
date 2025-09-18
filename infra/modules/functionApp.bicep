@description('Function App name')
param name string
@description('Location')
param location string
@description('Blob service base URL')
param storageAccountUrl string
@description('Storage account name (for AzureWebJobsStorage hierarchical identity settings)')
param storageAccountName string
@description('Queue service base URL (for identity-based host storage)')
param storageQueueUrl string = ''
@description('Table service base URL (optional for identity-based host storage)')
param storageTableUrl string = ''
@description('Container name')
param blobContainer string
@description('Max bytes')
param maxBytes int
@description('Secret hash')
param internalUploadKeySha256 string
@description('Allowed context types CSV')
param allowedContextTypes string
@description('Log level')
param logLevel string = 'INFO'
@description('Include App Insights connection string if provided')
param appInsightsConnectionString string = ''
@description('Tags object')
param tags object = {}

@description('Consumption plan always; function runtime version set via property')
var functionsExtensionVersion = '~4'

// Identity-only storage: no key-based AzureWebJobsStorage connection string supported anymore.

@description('App Service Plan resource ID (Linux B1) to host this Function App')
param planId string

// (Note) storage account id constructed in main for role assignment; not needed directly here.

// Derived app settings arrays for cleaner conditional logic
var baseAppSettings = [
  {
    name: 'STORAGE_ACCOUNT_URL'
    value: storageAccountUrl
  }
  {
    name: 'BLOB_CONTAINER'
    value: blobContainer
  }
  {
    name: 'MAX_BYTES'
    value: string(maxBytes)
  }
  {
    name: 'INTERNAL_UPLOAD_KEY_SHA256'
    value: internalUploadKeySha256
  }
  {
    name: 'ALLOWED_CONTEXT_TYPES'
    value: allowedContextTypes
  }
  {
    name: 'LOG_LEVEL'
    value: logLevel
  }
  {
    name: 'FUNCTIONS_WORKER_RUNTIME'
    value: 'python'
  }
  {
    name: 'FUNCTIONS_EXTENSION_VERSION'
    value: functionsExtensionVersion
  }
  {
    name: 'WEBSITE_RUN_FROM_PACKAGE'
    value: '1'
  }
]
var identityBlobSettings = [
  {
    name: 'AzureWebJobsStorage__blobServiceUri'
    value: storageAccountUrl
  }
  {
    name: 'AzureWebJobsStorage__credential'
    value: 'ManagedIdentity'
  }
]
var identityAccountSetting = [
  {
    name: 'AzureWebJobsStorage__accountName'
    value: storageAccountName
  }
]
var identityQueueSetting = !empty(storageQueueUrl) ? [
  {
    name: 'AzureWebJobsStorage__queueServiceUri'
    value: storageQueueUrl
  }
  // If table access required in future add AzureWebJobsStorage__tableServiceUri
] : []
var identityTableSetting = !empty(storageTableUrl) ? [
  {
    name: 'AzureWebJobsStorage__tableServiceUri'
    value: storageTableUrl
  }
] : []
var appInsightsSetting = empty(appInsightsConnectionString) ? [] : [
  {
    name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    value: appInsightsConnectionString
  }
]

// Function App on existing dedicated Linux plan (B1). Using plan instead of consumption due to Linux dynamic worker restriction.
resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: name
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    httpsOnly: true
    serverFarmId: planId
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: concat(
        baseAppSettings,
        identityAccountSetting,
        identityBlobSettings,
        identityQueueSetting,
        identityTableSetting,
        appInsightsSetting
      )
      ftpsState: 'FtpsOnly'
    }
  }
  tags: tags
}

output principalId string = functionApp.identity.principalId
output hostname string = functionApp.properties.defaultHostName
