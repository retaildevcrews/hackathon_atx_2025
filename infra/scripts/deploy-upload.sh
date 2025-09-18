#!/usr/bin/env bash
set -euo pipefail

RG="${RG:-2025_hackathon}"
LOCATION="${LOCATION:-eastus2}"
PARAMS_FILE="${PARAMS_FILE:-../params.dev.json}"
SECRET="${SECRET:-}"
BYPASS="${BYPASS:-false}"
SKIP_SECOND="${SKIP_SECOND:-false}"

if ! command -v az >/dev/null 2>&1; then
  echo "Azure CLI (az) not found" >&2; exit 1; fi
if [ ! -f "$PARAMS_FILE" ]; then
  echo "Params file not found: $PARAMS_FILE" >&2; exit 1; fi
if [ -z "$SECRET" ] && [ "$BYPASS" != "true" ]; then
  echo "Provide SECRET env var or set BYPASS=true" >&2; exit 1; fi

if [ -n "$SECRET" ]; then
  HASH=$(printf "%s" "$SECRET" | openssl dgst -sha256 | awk '{print $2}')
else
  HASH="noop"
fi

AZWJ=$(jq -r '.parameters.azureWebJobsStorage.value' "$PARAMS_FILE")

echo "First pass deployment..."
FIRST=$(az deployment group create \
  -g "$RG" \
  -f ../main.bicep \
  -p @"$PARAMS_FILE" \
  -p internalUploadKeySha256="$HASH" \
  -p azureWebJobsStorage="$AZWJ" \
  --query properties.outputs -o json)

FUNC_PID=$(echo "$FIRST" | jq -r '.functionPrincipalId.value')
WEB_PID=$(echo "$FIRST" | jq -r '.webPrincipalId.value')
FUNC_ENDPOINT=$(echo "$FIRST" | jq -r '.functionEndpoint.value')

echo "Function Endpoint: $FUNC_ENDPOINT"
echo "Function PrincipalId: $FUNC_PID"
echo "Web PrincipalId: $WEB_PID"

if [ "$SKIP_SECOND" = "true" ]; then
  exit 0
fi

echo "Second pass..."
az deployment group create \
  -g "$RG" \
  -f ../main.bicep \
  -p @"$PARAMS_FILE" \
  -p internalUploadKeySha256="$HASH" \
  -p azureWebJobsStorage="$AZWJ" \
  -p functionPrincipalId="$FUNC_PID" \
  -p webPrincipalId="$WEB_PID" \
  --query properties.outputs -o json >/dev/null

echo "Deployment complete. Upload URL: $FUNC_ENDPOINT"
[ "$BYPASS" = "true" ] && echo "WARNING: Bypass mode requested; ensure function configured." >&2
