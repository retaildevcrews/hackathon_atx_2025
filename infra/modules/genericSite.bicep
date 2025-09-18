@description('Generic Linux Web App name')
param name string
@description('Location')
param location string
@description('App Service Plan resource id')
param planId string
@description('Tags object')
param tags object = {}

// Simple generic Linux web app (code-based) with Python runtime placeholder.
// We will override to container using deployment scripts (az webapp config container set) later if desired.
// Keeping a runtime here allows immediate provisioning without container image requirement.
resource site 'Microsoft.Web/sites@2023-12-01' = {
  name: name
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    httpsOnly: true
    serverFarmId: planId
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      ftpsState: 'Disabled'
    }
  }
  tags: tags
}

output principalId string = site.identity.principalId
output hostname string = site.properties.defaultHostName
output nameOut string = site.name
