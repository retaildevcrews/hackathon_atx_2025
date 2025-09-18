@description('Deployment location')
param location string
@description('Environment label (e.g. dev, test, prod)')
param env string = 'dev'
@description('Existing storage account name used for blob uploads & WebJobs host')
param storageAccountName string
@description('Blob container name for uploads')
param blobContainer string = 'uploads'
@description('Hash of internal shared secret')
param internalUploadKeySha256 string
@description('Max upload bytes')
param maxBytes int = 10485760
@description('Allowed context types CSV')
param allowedContextTypes string = 'candidate,decision-kit'
@description('Log level')
param logLevel string = 'INFO'
@description('App Service Plan SKU for web app (Basic B1 default)')
param webPlanSku string = 'B1'
@description('Name prefix base (company/project)')
param namePrefix string = 'atxhack2025'
@description('AzureWebJobsStorage connection string to existing storage (pass via parameter or key vault ref)')
@secure()
param azureWebJobsStorage string

@description('Optional pre-known Function App principalId for role assignment (2nd pass)')
param functionPrincipalId string = ''
@description('Optional pre-known Web App principalId for role assignment (2nd pass)')
param webPrincipalId string = ''

// Derived identifiers
// Existing storage account (assumed same resource group). For cross-RG, separate deployment or module needed.
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

var storageDnsSuffix = environment().suffixes.storage
var storageAccountUrl = 'https://${storageAccountName}.blob.${storageDnsSuffix}'

// Resource naming (avoid >24 char limits for some; kept concise)
var aiName = '${namePrefix}ai'
var planName = '${namePrefix}plan'
var webName = '${namePrefix}web'
var funcName = '${namePrefix}func'

// Module: App Insights (always deployed to avoid conditional output access issues)
module appInsights 'modules/appInsights.bicep' = {
  name: 'appInsightsDeploy'
  params: {
    name: aiName
    location: location
    tags: {
      env: env
      component: 'observability'
    }
  }
}

// Module: Service Plan for Web App
module svcPlan 'modules/servicePlan.bicep' = {
  name: 'servicePlanDeploy'
  params: {
    name: planName
    location: location
    skuName: webPlanSku
    tags: {
      env: env
      component: 'web'
    }
  }
}

// Module: Web App (API/UI placeholder)
module webApp 'modules/webApp.bicep' = {
  name: 'webAppDeploy'
  params: {
    name: webName
    location: location
    planId: svcPlan.outputs.planId
    storageAccountUrl: storageAccountUrl
    blobContainer: blobContainer
    maxBytes: maxBytes
    internalUploadKeySha256: internalUploadKeySha256
    allowedContextTypes: allowedContextTypes
    logLevel: logLevel
  appInsightsConnectionString: appInsights.outputs.connectionString
    tags: {
      env: env
      component: 'web'
    }
  }
}

// Module: Function App (consumption)
module functionApp 'modules/functionApp.bicep' = {
  name: 'functionAppDeploy'
  params: {
    name: funcName
    location: location
    storageAccountUrl: storageAccountUrl
    blobContainer: blobContainer
    maxBytes: maxBytes
    internalUploadKeySha256: internalUploadKeySha256
    allowedContextTypes: allowedContextTypes
    logLevel: logLevel
  appInsightsConnectionString: appInsights.outputs.connectionString
    azureWebJobsStorage: azureWebJobsStorage
    tags: {
      env: env
      component: 'function'
    }
  }
}

// Role Definitions
var blobDataContributor = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

// Optional inline role assignments (2nd pass) using provided principalIds.
// Rationale: system-assigned identity principalId is not available for deterministic name at compile time; supply via parameters on 2nd deployment.

resource functionBlobContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(functionPrincipalId)) {
  name: guid(storageAccount.id, functionPrincipalId, 'blob-data-contributor-func')
  scope: storageAccount
  properties: {
    principalId: functionPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobDataContributor)
    principalType: 'ServicePrincipal'
  }
}

resource webBlobContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(webPrincipalId)) {
  name: guid(storageAccount.id, webPrincipalId, 'blob-data-contributor-web')
  scope: storageAccount
  properties: {
    principalId: webPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobDataContributor)
    principalType: 'ServicePrincipal'
  }
}

output functionEndpoint string = 'https://${functionApp.outputs.hostname}/api/upload'
output webEndpoint string = 'https://${webApp.outputs.hostname}'
output functionPrincipalId string = functionApp.outputs.principalId
output webPrincipalId string = webApp.outputs.principalId
output storageAccountBlobUrl string = storageAccountUrl
output appInsightsConnectionString string = appInsights.outputs.connectionString
