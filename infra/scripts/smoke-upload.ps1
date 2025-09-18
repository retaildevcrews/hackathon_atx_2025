Param(
  [string]$FunctionUrl,  # e.g. https://xyzfunc.azurewebsites.net/api/upload
  [string]$Secret,
  [string]$ContextType = 'candidate',
  [string]$ContextId = 'smoke',
  [string]$FilePath = '../README.md'
)

if (-not $FunctionUrl) { throw 'FunctionUrl required' }
if (-not (Test-Path $FilePath)) { throw "File not found: $FilePath" }

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"
$fileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $FilePath))
$filename = [System.IO.Path]::GetFileName($FilePath)

$pre = "--$boundary$LF" +
  "Content-Disposition: form-data; name=\"contextType\"$LF$LF$ContextType$LF" +
  "--$boundary$LF" +
  "Content-Disposition: form-data; name=\"contextId\"$LF$LF$ContextId$LF" +
  "--$boundary$LF" +
  "Content-Disposition: form-data; name=\"file\"; filename=\"$($filename)\"$LF" +
  "Content-Type: application/octet-stream$LF$LF"
$post = "$LF--$boundary--$LF"

$preBytes = [System.Text.Encoding]::UTF8.GetBytes($pre)
$postBytes = [System.Text.Encoding]::UTF8.GetBytes($post)

$bodyBytes = New-Object System.IO.MemoryStream
$bodyBytes.Write($preBytes,0,$preBytes.Length) | Out-Null
$bodyBytes.Write($fileBytes,0,$fileBytes.Length) | Out-Null
$bodyBytes.Write($postBytes,0,$postBytes.Length) | Out-Null
$bodyBytes.Position = 0

$headers = @{ 'Content-Type' = "multipart/form-data; boundary=$boundary" }
if ($Secret) { $headers['X-Internal-Upload-Key'] = $Secret }

$response = Invoke-WebRequest -Uri $FunctionUrl -Method POST -Headers $headers -Body $bodyBytes.ToArray()
Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
Write-Host $response.Content
