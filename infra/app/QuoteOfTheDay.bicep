param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string
param applicationInsightsName string
@secure()
param appDefinition object
param appConfigurationConnectionString string
param appServicePlanId string

param appCommandLine string = '"entrypoint.sh"'


param runtimeName string = 'python'
param runtimeVersion string = '3.12'

param runtimeNameAndVersion string = '${runtimeName}|${runtimeVersion}'
param alwaysOn bool = true
param linuxFxVersion string = runtimeNameAndVersion
param minimumElasticInstanceCount int = -1
param numberOfWorkers int = -1
param use32BitWorkerProcess bool = false
param ftpsState string = 'FtpsOnly'

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: name
  location: location
  tags: union(tags, {'azd-service-name':  'QuoteOfTheDay' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identity.id}': {} }
  }
  properties: {
    serverFarmId: appServicePlanId
    siteConfig: {
      linuxFxVersion: linuxFxVersion
      alwaysOn: alwaysOn
      ftpsState: ftpsState
      minTlsVersion: '1.2'
      appCommandLine: appCommandLine
      numberOfWorkers: numberOfWorkers != -1 ? numberOfWorkers : null
      minimumElasticInstanceCount: minimumElasticInstanceCount != -1 ? minimumElasticInstanceCount : null
      use32BitWorkerProcess: use32BitWorkerProcess
    }
  }
}

module configAppSettings '../shared/appservice-appsettings.bicep' = {
  name: '${name}-appSettings'
  params: {
    name: appService.name
    appSettings: union(
      {
        ApplicationInsightsConnectionString: applicationInsights.properties.ConnectionString
      },
      {
        ENABLE_ORYX_BUILD: true
      },
      {
        SCM_DO_BUILD_DURING_DEPLOYMENT: false
      },
      {
        AzureAppConfigurationConnectionString: appConfigurationConnectionString
      },
      appDefinition.settings)
  }
}

output name string = appService.name
output uri string = 'https://${appService.properties.defaultHostName}'
