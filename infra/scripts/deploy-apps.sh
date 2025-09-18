#!/usr/bin/env bash
set -euo pipefail

usage(){
  echo "Usage: $0 -g <resourceGroup> -f <functionApp> -a <apiApp> -w <webApp> -r <acrName> [--bypass] [-t <tag>]" >&2
}

RG=""; FUNC=""; API=""; WEB=""; ACR=""; TAG=""; BYPASS=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--resource-group) RG="$2"; shift 2;;
    -f|--function-app) FUNC="$2"; shift 2;;
    -a|--api-app) API="$2"; shift 2;;
    -w|--web-app) WEB="$2"; shift 2;;
    -r|--acr) ACR="$2"; shift 2;;
    -t|--tag) TAG="$2"; shift 2;;
    --bypass) BYPASS=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done
[[ -z "$RG" || -z "$FUNC" || -z "$API" || -z "$WEB" || -z "$ACR" ]] && { usage; exit 1; }

if [[ -z "$TAG" ]]; then
  TAG=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)
fi
echo "[INFO] Using tag: $TAG"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
pushd "$SCRIPT_DIR" >/dev/null
./deploy-function-code.sh -g "$RG" -f "$FUNC" ${BYPASS:+--bypass}
./deploy-criteria-api.sh -g "$RG" -a "$API" -r "$ACR" -t "$TAG"
./deploy-webapp.sh -g "$RG" -w "$WEB" -r "$ACR" -t "$TAG"
popd >/dev/null
