Param(
  [string]$ResourceGroup = '2025_hackathon',
  [string]$Location = 'eastus2',
  [string]$ParamsFile = '../params.dev.json',
  [string]$Secret,              # raw shared secret
  [switch]$BypassAuth,          # sets DISABLE_INTERNAL_UPLOAD_AUTH on function app after deploy
  [switch]$SkipSecondPass
)

if (-not (Get-Command az -ErrorAction SilentlyContinue)) { throw 'Azure CLI (az) not found in PATH.' }

if (-not (Test-Path $ParamsFile)) { throw "Params file not found: $ParamsFile" }

# Read params file JSON (expects azureWebJobsStorage parameter)
$paramsJson = Get-Content -Raw -Path $ParamsFile | ConvertFrom-Json
$azureWebJobsStorage = $paramsJson.parameters.azureWebJobsStorage.value
if (-not $azureWebJobsStorage) { throw 'azureWebJobsStorage value missing in params file' }

if (-not $Secret -and -not $BypassAuth) {
  throw 'Provide -Secret or use -BypassAuth for demo.'
}

function Get-Sha256Hex($text) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
  $sha = [System.Security.Cryptography.SHA256]::Create()
  $hash = $sha.ComputeHash($bytes)
  -join ($hash | ForEach-Object { $_.ToString('x2') })
}

$hash = if ($Secret) { Get-Sha256Hex $Secret } else { 'noop' }

Write-Host "First pass deployment..." -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$infraRoot = Resolve-Path (Join-Path $scriptDir '..')
$mainFile = Join-Path $infraRoot 'main.bicep'
if (-not (Test-Path $mainFile)) { throw "Cannot locate main.bicep at $mainFile" }
$resolvedParams = if ([System.IO.Path]::IsPathRooted($ParamsFile)) { $ParamsFile } else { (Resolve-Path (Join-Path (Get-Location) $ParamsFile)) }

Write-Host "Using main file: $mainFile" -ForegroundColor DarkCyan
Write-Host "Using params file: $resolvedParams" -ForegroundColor DarkCyan

$first = az deployment group create `
  -g $ResourceGroup `
  -f $mainFile `
  -p @$resolvedParams `
  -p internalUploadKeySha256=$hash `
  -p azureWebJobsStorage="$azureWebJobsStorage" `
  --query properties.outputs -o json

if ($LASTEXITCODE -ne 0) { throw 'First pass deployment failed.' }

$firstObj = $first | ConvertFrom-Json
$funcPid = $firstObj.functionPrincipalId.value
$webPid = $firstObj.webPrincipalId.value
$funcEndpoint = $firstObj.functionEndpoint.value

Write-Host "Function Endpoint: $funcEndpoint" -ForegroundColor Green
Write-Host "Function PrincipalId: $funcPid" -ForegroundColor DarkGray
Write-Host "Web PrincipalId: $webPid" -ForegroundColor DarkGray

if ($SkipSecondPass) { return }

Write-Host "Second pass (role assignments)..." -ForegroundColor Cyan
$second = az deployment group create `
  -g $ResourceGroup `
  -f $mainFile `
  -p @$resolvedParams `
  -p internalUploadKeySha256=$hash `
  -p azureWebJobsStorage="$azureWebJobsStorage" `
  -p functionPrincipalId=$funcPid `
  -p webPrincipalId=$webPid `
  --query properties.outputs -o json

if ($LASTEXITCODE -ne 0) { throw 'Second pass deployment failed.' }

Write-Host "Deployment complete." -ForegroundColor Green
Write-Host "Upload URL: $funcEndpoint" -ForegroundColor Green

if ($BypassAuth) {
  Write-Host 'Setting DISABLE_INTERNAL_UPLOAD_AUTH=1 on Function App...' -ForegroundColor Yellow
  # derive function app name from endpoint host (https://name.azurewebsites.net/...)
  $uri = [System.Uri]$funcEndpoint
  $hostParts = $uri.Host.Split('.')
  $funcAppName = $hostParts[0]
  az functionapp config appsettings set -g $ResourceGroup -n $funcAppName --settings DISABLE_INTERNAL_UPLOAD_AUTH=true | Out-Null
  Write-Warning 'Bypass auth ENABLED. Do NOT use in production environments.'
}
