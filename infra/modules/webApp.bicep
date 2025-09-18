@description('Web App name')
param name string
@description('Location')
param location string
@description('App Service Plan name (resource ID or name in same group)')
param planId string
@description('Storage account blob service URL (e.g. https://<account>.<dnsSuffix>) where dnsSuffix from environment().')
param storageAccountUrl string
@description('Upload container name')
param blobContainer string
@description('Max bytes int')
param maxBytes int
@description('Hash of shared secret')
param internalUploadKeySha256 string
@description('Allowed context types CSV')
param allowedContextTypes string
@description('Log level')
param logLevel string = 'INFO'
@description('Tags object')
param tags object = {}
@description('Optional App Insights connection string')
param appInsightsConnectionString string = ''

// Base app settings array (always included)
var baseSettings = [
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
]

// Optional AI connection string
var aiSetting = empty(appInsightsConnectionString) ? [] : [
  {
    name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
    value: appInsightsConnectionString
  }
]

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: name
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: planId
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: concat(baseSettings, aiSetting)
    }
  }
  tags: tags
}

output principalId string = webApp.identity.principalId
output nameOut string = webApp.name
output hostname string = webApp.properties.defaultHostName
