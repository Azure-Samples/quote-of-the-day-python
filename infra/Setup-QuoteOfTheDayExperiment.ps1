param(
    [Parameter(Mandatory=$True)]
    [string]
    $SubscriptionId,
    
    [Parameter(Mandatory=$True)]
    [string]
    $AppConfigurationName)

function Setup-QuoteOfTheDayExperiment($subscriptionId, $appConfigurationName)
{
    az account show >$null 2>$null

    if ($LASTEXITCODE -ne 0)
    {
        az login
    }
    
    az account set --subscription $SubscriptionId

}

Setup-QuoteOfTheDayExperiment $SubscriptionId $AppConfigurationName
