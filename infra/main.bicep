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
// Identity-only storage: AzureWebJobsStorage key-based connection removed. Host will use managed identity & hierarchical settings.

@description('Optional pre-known Function App principalId for role assignment (2nd pass)')
param functionPrincipalId string = ''
@description('Optional pre-known Web App principalId for role assignment (2nd pass)')
param webPrincipalId string = ''
@description('Optional pre-known API App principalId for role assignment (2nd pass)')
param apiPrincipalId string = ''
@description('Optional pre-known UI App principalId for role assignment (2nd pass)')
param uiPrincipalId string = ''
@description('Container Registry name (will be created)')
param acrName string = '${namePrefix}acr'
@description('Container Registry SKU')
param acrSku string = 'Basic'

// Derived identifiers
// Existing storage account (assumed same resource group). For cross-RG, separate deployment or module needed.
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

var storageDnsSuffix = environment().suffixes.storage
var storageAccountUrl = 'https://${storageAccountName}.blob.${storageDnsSuffix}'
var storageQueueUrl = 'https://${storageAccountName}.queue.${storageDnsSuffix}'
var storageTableUrl = 'https://${storageAccountName}.table.${storageDnsSuffix}'

// Resource naming (avoid >24 char limits for some; kept concise)
var aiName = '${namePrefix}ai'
var planName = '${namePrefix}plan'
var webName = '${namePrefix}web'
var funcName = '${namePrefix}func'
var apiName = '${namePrefix}api'
var uiName = '${namePrefix}ui'

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
    planId: svcPlan.outputs.planId
    storageAccountName: storageAccountName
  storageAccountUrl: storageAccountUrl
  storageQueueUrl: storageQueueUrl
    storageTableUrl: storageTableUrl
    blobContainer: blobContainer
    maxBytes: maxBytes
    internalUploadKeySha256: internalUploadKeySha256
    allowedContextTypes: allowedContextTypes
    logLevel: logLevel
  appInsightsConnectionString: appInsights.outputs.connectionString
    tags: {
      env: env
      component: 'function'
    }
  }
}

// Container Registry (for API & UI images)
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    env: env
    component: 'registry'
  }
}

// Generic API App (will be converted to container via deployment scripts)
module apiApp 'modules/genericSite.bicep' = {
  name: 'apiAppDeploy'
  params: {
    name: apiName
    location: location
    planId: svcPlan.outputs.planId
    tags: {
      env: env
      component: 'api'
    }
  }
}

// Generic UI App (will serve React build via container)
module uiApp 'modules/genericSite.bicep' = {
  name: 'uiAppDeploy'
  params: {
    name: uiName
    location: location
    planId: svcPlan.outputs.planId
    tags: {
      env: env
      component: 'ui'
    }
  }
}

// Role Definitions
var blobDataContributor = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var queueDataContributor = '974c5e8b-45b9-4653-ba55-5f855dd0fb88'
var acrPullRole = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

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

// Queue data contributor for host lease operations (identity-based AzureWebJobsStorage)
resource functionQueueContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(functionPrincipalId)) {
  name: guid(storageAccount.id, functionPrincipalId, 'queue-data-contributor-func')
  scope: storageAccount
  properties: {
    principalId: functionPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', queueDataContributor)
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

resource apiBlobContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(apiPrincipalId)) {
  name: guid(storageAccount.id, apiPrincipalId, 'blob-data-contributor-api')
  scope: storageAccount
  properties: {
    principalId: apiPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobDataContributor)
    principalType: 'ServicePrincipal'
  }
}

resource uiBlobContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(uiPrincipalId)) {
  name: guid(storageAccount.id, uiPrincipalId, 'blob-data-contributor-ui')
  scope: storageAccount
  properties: {
    principalId: uiPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobDataContributor)
    principalType: 'ServicePrincipal'
  }
}

// ACR Pull role assignments (2nd pass) for identities to pull private images
resource webAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(webPrincipalId)) {
  name: guid(acr.id, webPrincipalId, 'acr-pull-web')
  scope: acr
  properties: {
    principalId: webPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRole)
    principalType: 'ServicePrincipal'
  }
}

resource apiAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(apiPrincipalId)) {
  name: guid(acr.id, apiPrincipalId, 'acr-pull-api')
  scope: acr
  properties: {
    principalId: apiPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRole)
    principalType: 'ServicePrincipal'
  }
}

resource uiAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(uiPrincipalId)) {
  name: guid(acr.id, uiPrincipalId, 'acr-pull-ui')
  scope: acr
  properties: {
    principalId: uiPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRole)
    principalType: 'ServicePrincipal'
  }
}

output functionEndpoint string = 'https://${functionApp.outputs.hostname}/api/upload'
output webEndpoint string = 'https://${webApp.outputs.hostname}'
output functionPrincipalId string = functionApp.outputs.principalId
output webPrincipalId string = webApp.outputs.principalId
output storageAccountBlobUrl string = storageAccountUrl
output appInsightsConnectionString string = appInsights.outputs.connectionString
output acrLoginServer string = acr.properties.loginServer
output apiPrincipalIdOut string = apiApp.outputs.principalId
output uiPrincipalIdOut string = uiApp.outputs.principalId
output apiHostname string = apiApp.outputs.hostname
output uiHostname string = uiApp.outputs.hostname

