param location string
param name string
param AACsku string
param AACsoftDeleteRetentionInDays int
param AACenablePurgeProtection bool
param AACdisableLocalAuth bool
param applicationInsightsId string

resource appConfigurationStore 'Microsoft.AppConfiguration/configurationStores@2023-09-01-preview' = {
  name: name
  location: location
  sku: {
    name: AACsku
  }
  properties: {
    softDeleteRetentionInDays: AACsoftDeleteRetentionInDays
    enablePurgeProtection: AACenablePurgeProtection
    disableLocalAuth: AACdisableLocalAuth
    telemetry: {
      resourceId: applicationInsightsId
    }
  }
}

resource SecretKey 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  name: 'SECRET_KEY'
  parent: appConfigurationStore
  properties: {
    value: 'fake-secret-key'
  }
}

resource SQLAlchemyDatabaseUri 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  name: 'SQLALCHEMY_DATABASE_URI'
  parent: appConfigurationStore
  properties: {
    value: 'sqlite:///db.sqlite'
  }
}

resource variantFeatureFlagGreeting 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  name: '.appconfig.featureflag~2FGreeting'
  parent: appConfigurationStore
  properties: {
    contentType: 'application/vnd.microsoft.appconfig.ff+json;charset=utf-8'
    value: '''
    {
      "id": "Greeting",
      "description": "",
      "enabled": true,
      "variants": [
        {
          "name": "Default"
        },
        {
          "name": "Simple",
          "configuration_value": "Hello!"
        },
        {
          "name": "Long",
          "configuration_value": "I hope this makes your day!"
        }
      ],
      "allocation": {
        "percentile": [
          {
            "variant": "Default",
            "from": 0,
            "to": 50
          },
          {
            "variant": "Simple",
            "from": 50,
            "to": 75
          },
          {
            "variant": "Long",
            "from": 75,
            "to": 100
          }
        ],
        "default_when_enabled": "Default",
        "default_when_disabled": "Default"
      },
      "telemetry": {
        "enabled": true
      }
    }
    '''
  }
}

var readonlyKey = filter(appConfigurationStore.listKeys().value, k => k.name == 'Primary Read Only')[0]

output appConfigurationConnectionString string = readonlyKey.connectionString
output appConfigurationName string = appConfigurationStore.name
