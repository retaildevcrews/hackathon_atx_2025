# Infrastructure (Bicep)

Provision Azure resources for the Generic Upload Function + placeholder Web App using existing Storage Account.

## Resources Deployed
- Application Insights (always)
- Linux App Service Plan (for Web App)
- Web App (Python 3.11) with system-assigned managed identity
- Function App (Python 3.11, Consumption) with system-assigned managed identity
- (Optional second-pass) Role Assignments: Storage Blob Data Contributor for both identities (two-step due to principalId timing)

## Two-Pass Role Assignment Pattern
1. First deployment: omit `functionPrincipalId` and `webPrincipalId` (parameters default to empty). Capture outputs.
2. Second deployment: pass those IDs back to create role assignments (Blob Data Contributor) to allow upload code to access the existing storage account.

Why? System-assigned identity object IDs are only known after resource creation— cannot use their principalId for deterministic roleAssignment name at compile-time.

## Parameters
| Name | Required | Default | Description |
| ---- | -------- | ------- | ----------- |
| location | yes | (none) | Azure region |
| env | no | dev | Environment label (tag only) |
| storageAccountName | yes | | Existing storage account (same RG) |
| blobContainer | no | uploads | Target upload container (must exist) |
| internalUploadKeySha256 | yes | | Hex SHA256 of shared secret |
| maxBytes | no | 10485760 | Max upload size in bytes |
| allowedContextTypes | no | candidate,decision-kit | CSV list |
| logLevel | no | INFO | Log level passed to apps |
| webPlanSku | no | B1 | App Service Plan SKU |
| namePrefix | no | atxhack2025 | Naming prefix (ai, plan, web, func appended) |
| (removed) azureWebJobsStorage | NO LONGER USED | | Replaced by managed identity + hierarchical settings (AzureWebJobsStorage__*) |
| functionPrincipalId | no | '' | Provided on second pass for role assignment |
| webPrincipalId | no | '' | Provided on second pass for role assignment |

## Outputs
| Output | Description |
| ------ | ----------- |
| functionEndpoint | Upload function endpoint URL |
| webEndpoint | Web app default hostname |
| functionPrincipalId | Captured system-assigned identity principalId |
| webPrincipalId | Captured system-assigned identity principalId |
| storageAccountBlobUrl | Base blob URL |
| appInsightsConnectionString | App Insights connection string |

## Example Parameter File (params.dev.json)
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": { "value": "eastus2" },
    "storageAccountName": { "value": "decisionkitstorage" },
    "internalUploadKeySha256": { "value": "<hex>" }
  }
}
```

### Identity-Based Host Storage
The Function App no longer accepts a `azureWebJobsStorage` connection string. Instead it sets hierarchical settings so the runtime uses Managed Identity:

App Settings applied:
```
AzureWebJobsStorage__accountName = <storageAccountName>
AzureWebJobsStorage__blobServiceUri = https://<account>.blob.<dnsSuffix>
AzureWebJobsStorage__queueServiceUri = https://<account>.queue.<dnsSuffix>
AzureWebJobsStorage__credential = ManagedIdentity
```
Required Role Assignments (granted in second pass):
* Storage Blob Data Contributor
* Storage Queue Data Contributor

If you add Tables in future, include:
```
AzureWebJobsStorage__tableServiceUri = https://<account>.table.<dnsSuffix>
```

## Deploy (First Pass)
```powershell
az deployment group what-if -g 2025_hackathon -f infra/main.bicep -p @infra/params.dev.json
az deployment group create -g 2025_hackathon -f infra/main.bicep -p @infra/params.dev.json
```
Capture the `functionPrincipalId` and `webPrincipalId` outputs.

## Deploy (Second Pass - Add Role Assignments)
```powershell
$funcPid = '<captured-func-principalId>'
$webPid = '<captured-web-principalId>'
az deployment group what-if -g 2025_hackathon -f infra/main.bicep -p @infra/params.dev.json functionPrincipalId=$funcPid webPrincipalId=$webPid
az deployment group create -g 2025_hackathon -f infra/main.bicep -p @infra/params.dev.json functionPrincipalId=$funcPid webPrincipalId=$webPid
```

## Naming Convention
Using prefix `atxhack2025`:
- App Insights: `atxhack2025ai`
- Plan: `atxhack2025plan`
- Web App: `atxhack2025web`
- Function App: `atxhack2025func`

## Notes / Future Enhancements
## Helper Scripts

Located in `infra/scripts/` to streamline common tasks.

### PowerShell Two-Pass Deployment
```
pwsh ./infra/scripts/deploy-upload.ps1 -ResourceGroup 2025_hackathon -Location eastus2 -ParamsFile ./infra/params.dev.json -Secret "raw-secret"
```
Second pass performed automatically unless `-SkipSecondPass` supplied. Use `-BypassAuth` (no secret) only for demo scenarios where the function is configured with `DISABLE_INTERNAL_UPLOAD_AUTH=true`.

### Bash Two-Pass Deployment (macOS/Linux)
```
cd infra/scripts
SECRET="raw-secret" ./deploy-upload.sh
```
Environment overrides: `RG`, `LOCATION`, `PARAMS_FILE`, `SECRET`, `BYPASS=true`, `SKIP_SECOND=true`.

### Smoke Test Upload (PowerShell)
After deployment (ensure role assignments propagated):
```
pwsh ./infra/scripts/smoke-upload.ps1 -FunctionUrl https://<func>.azurewebsites.net/api/upload -Secret "raw-secret" -FilePath README.md
```
Outputs status and JSON response. Omit `-Secret` ONLY if bypass mode enabled (unsafe for shared envs).

### Propagation Note
Role assignments may take up to ~60s to grant blob & queue access. If initial upload returns 403 on host logs (lease acquisition) or function invocation, wait and retry. The host lock error:
`failed to acquire host lock lease: Status: 403` indicates the queue permission (Storage Queue Data Contributor) or hierarchical settings were not yet applied/propagated.

- Cross-RG existing storage: would require a separate subscription-scope or RG module approach.
- Key Vault: move `INTERNAL_UPLOAD_KEY_SHA256` & connection strings to secrets.
- Add diagnostic settings to Log Analytics workspace.
- Add optional container deployment toggle for Function App.

## Cleanup
```powershell
az group delete -n 2025_hackathon --yes --no-wait
```
