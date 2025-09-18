@description('Function App name')
param name string
@description('Location')
param location string
@description('Blob service base URL')
param storageAccountUrl string
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

@description('AzureWebJobsStorage connection string (for now required by Functions host)')
param azureWebJobsStorage string

// (Note) storage account id constructed in main for role assignment; not needed directly here.

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: name
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    httpsOnly: true
    siteConfig: {
      appSettings: concat([
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
          name: 'AzureWebJobsStorage'
          value: azureWebJobsStorage
        }
      ], empty(appInsightsConnectionString) ? [] : [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
      ])
      linuxFxVersion: 'Python|3.11'
      ftpsState: 'Disabled'
    }
    serverFarmId: '' // Implicit consumption plan; leave empty for Y1 dynamic
  }
  tags: tags
}

output principalId string = functionApp.identity.principalId
output hostname string = functionApp.properties.defaultHostName
