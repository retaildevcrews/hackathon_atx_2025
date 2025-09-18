@description('Name of the App Service Plan')
param name string
@description('Azure region')
param location string
@description('SKU name (e.g., B1, S1)')
param skuName string = 'B1'
@description('Tags object')
param tags object = {}

// NOTE: Linux App Service does NOT support Free (F1) or Shared (D1) tiers.
// If you pass F1 or D1 here deployment will fail. B1 is the lowest-cost Linux option.

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: name
  location: location
  sku: {
    name: skuName
    tier: toLower(skuName) == 'b1' ? 'Basic' : ''
    size: skuName
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
  tags: tags
}

output planId string = plan.id
output planName string = plan.name
