#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage(){
  cat >&2 <<EOF
Usage: $(basename "$0") [options]
Options:
  -g, --resource-group <rg>      Resource group (default env RG or 2025_hackathon)
  -l, --location <loc>           Location (default eastus2)
  -p, --params <file>            Parameters file (default params.dev.json adjacent to main.bicep)
  --secret <value>               Raw shared secret (hash stored as setting)
  --bypass                       Enable DISABLE_INTERNAL_UPLOAD_AUTH (demo mode)
  --skip-second                  Skip second pass role assignment
  --code                         Deploy function code (calls deploy-function-code.sh)
  --project <path>               Function project path (default apps/functions)
  --smoke                        Run smoke-upload.sh after deployment (implies --code if zip not yet deployed)
  --function-name <name>         Explicit function app name (otherwise derived from endpoint)
  -h, --help                     Show this help
Env Overrides: RG, LOCATION, PARAMS_FILE, SECRET, BYPASS, SKIP_SECOND, DEPLOY_CODE, SMOKE, PROJECT
EOF
}

RG="${RG:-2025_hackathon}"
LOCATION="${LOCATION:-eastus2}"
PARAMS_FILE="${PARAMS_FILE:-$SCRIPT_DIR/../params.dev.json}"
SECRET="${SECRET:-}"
BYPASS="${BYPASS:-false}"
SKIP_SECOND="${SKIP_SECOND:-false}"
DEPLOY_CODE=${DEPLOY_CODE:-false}
SMOKE=${SMOKE:-false}
PROJECT="${PROJECT:-$SCRIPT_DIR/../../apps/functions}"
FUNC_NAME="" # optional override

while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--resource-group) RG="$2"; shift 2;;
    -l|--location) LOCATION="$2"; shift 2;;
    -p|--params) PARAMS_FILE="$2"; shift 2;;
    --secret) SECRET="$2"; shift 2;;
    --bypass) BYPASS=true; shift;;
    --skip-second) SKIP_SECOND=true; shift;;
    --code) DEPLOY_CODE=true; shift;;
    --project) PROJECT="$2"; shift 2;;
    --smoke) SMOKE=true; shift;;
    --function-name) FUNC_NAME="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1" >&2; usage; exit 1;;
  esac
done

main_bicep="$SCRIPT_DIR/../main.bicep"

err(){ echo -e "\e[31m[ERROR]\e[0m $*" >&2; exit 1; }
info(){ echo -e "\e[36m[INFO]\e[0m  $*" >&2; }
warn(){ echo -e "\e[33m[WARN]\e[0m  $*" >&2; }

command -v az >/dev/null || err "Azure CLI (az) not found in PATH"
[[ -f "$main_bicep" ]] || err "main.bicep not found at $main_bicep"

# Resolve params path robustly: allow invocation from any cwd & guard against accidental double relative paths
if [[ ! -f "$PARAMS_FILE" ]]; then
  # If it's relative (no leading / or drive letter on Windows Git Bash) try script-relative combination
  case "$PARAMS_FILE" in
    /*|[A-Za-z]:/*) : ;; # absolute (Unix or Windows path) leave as is
    *)
      alt="$SCRIPT_DIR/$(basename "$PARAMS_FILE")"
      if [[ -f "$alt" ]]; then
        info "Params file not found at provided path '$PARAMS_FILE', using '$alt' instead.";
        PARAMS_FILE="$alt"
      fi
      ;;
  esac
fi
if [[ ! -f "$PARAMS_FILE" ]]; then
  warn "Diagnostics: script dir=$SCRIPT_DIR; attempted PARAMS_FILE=$PARAMS_FILE";
  err "Params file not found: $PARAMS_FILE"
fi

if [[ -z "$SECRET" && "$BYPASS" != true ]]; then
  err "Provide --secret or use --bypass for demo mode."
fi

if [[ -n "$SECRET" ]]; then
  HASH=$(printf "%s" "$SECRET" | openssl dgst -sha256 | awk '{print $2}')
else
  HASH="noop"
fi

info "First pass deployment (infrastructure without role bindings)..."
OUT_LINE=$(az deployment group create \
  -g "$RG" \
  -f "$main_bicep" \
  -p @"$PARAMS_FILE" \
  -p internalUploadKeySha256="$HASH" \
  --query "{f:properties.outputs.functionPrincipalId.value, w:properties.outputs.webPrincipalId.value, api:properties.outputs.apiPrincipalIdOut.value, ui:properties.outputs.uiPrincipalIdOut.value, e:properties.outputs.functionEndpoint.value}" -o tsv)

IFS=$'\t' read -r FUNC_PID WEB_PID API_PID UI_PID FUNC_ENDPOINT <<< "$OUT_LINE"

[[ -n "${FUNC_PID:-}" ]] || err "Missing function principal id in first pass output"
[[ -n "${WEB_PID:-}" ]] || err "Missing web principal id in first pass output"
[[ -n "${FUNC_ENDPOINT:-}" ]] || err "Missing function endpoint in first pass output"

info "Function Endpoint: $FUNC_ENDPOINT"
info "Function PrincipalId: $FUNC_PID"
info "Web PrincipalId: $WEB_PID"
[[ -n "${API_PID:-}" ]] && info "API PrincipalId: $API_PID"
[[ -n "${UI_PID:-}" ]] && info "UI PrincipalId: $UI_PID"

if [[ "$SKIP_SECOND" == true ]]; then
  info "Skipping second pass per request."
else
  info "Second pass (role assignments)..."
  SECOND_ARGS=( -g "$RG" -f "$main_bicep" -p @"$PARAMS_FILE" -p internalUploadKeySha256="$HASH" -p functionPrincipalId="$FUNC_PID" -p webPrincipalId="$WEB_PID" )
  [[ -n "${API_PID:-}" ]] && SECOND_ARGS+=( -p apiPrincipalId="$API_PID" )
  [[ -n "${UI_PID:-}" ]] && SECOND_ARGS+=( -p uiPrincipalId="$UI_PID" )
  az deployment group create "${SECOND_ARGS[@]}" --query properties.outputs -o none
fi

# Derive function app name if not provided
if [[ -z "$FUNC_NAME" ]]; then
  hostpart=$(printf '%s' "$FUNC_ENDPOINT" | sed -E 's#https?://([^/]+)/.*#\1#')
  FUNC_NAME=${hostpart%%.*}
fi
info "Function App Name: $FUNC_NAME"

if [[ "$BYPASS" == true ]]; then
  warn "Enabling DISABLE_INTERNAL_UPLOAD_AUTH (bypass) on $FUNC_NAME"
  az functionapp config appsettings set -g "$RG" -n "$FUNC_NAME" --settings DISABLE_INTERNAL_UPLOAD_AUTH=true >/dev/null
fi

# Optional code deploy
if [[ "$DEPLOY_CODE" == true ]]; then
  info "Deploying function code (project: $PROJECT)..."
  (cd "$SCRIPT_DIR" && ./deploy-function-code.sh -g "$RG" -f "$FUNC_NAME" -p "$PROJECT" $( [[ "$BYPASS" == true ]] && echo "--bypass" ))
fi

UPLOAD_URL="$FUNC_ENDPOINT"
info "Infrastructure complete. Upload URL: $UPLOAD_URL"

# Optional smoke test
if [[ "$SMOKE" == true ]]; then
  info "Running smoke test..."
  (cd "$SCRIPT_DIR" && ./smoke-upload.sh -u "$UPLOAD_URL") || err "Smoke test failed"
  info "Smoke test passed."
fi

info "Done."

