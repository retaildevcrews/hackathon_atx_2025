@description('Principal Id (object id) of identity to assign role to')
param principalId string
@description('Scope resource id')
param scope string
@description('Role definition id (GUID)')
param roleDefinitionId string
@description('Deterministic seed components for guid')
param seed string

var roleAssignmentName = guid(scope, principalId, seed)

resource assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  name: roleAssignmentName
  scope: resourceId('', '') // placeholder to enable module usage in main via extension resource pattern
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
    principalType: 'ServicePrincipal'
  }
}

output name string = assignment.name
