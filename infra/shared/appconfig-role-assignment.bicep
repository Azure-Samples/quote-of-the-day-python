param appConfigurationName string
param principalId string

var appConfigDataReaderRoleId = '516239f1-63e1-4d78-a4de-a74fb236a071'

resource appConfigurationStore 'Microsoft.AppConfiguration/configurationStores@2023-09-01-preview' existing = {
  name: appConfigurationName
}

// App Configuration Data Reader role assignment scoped to the App Configuration resource
resource appConfigRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appConfigurationStore.id, principalId, appConfigDataReaderRoleId)
  scope: appConfigurationStore
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', appConfigDataReaderRoleId)
    principalType: 'ServicePrincipal'
  }
}
