#!/usr/bin/env bash
set -euo pipefail

usage(){
  echo "Usage: $0 -g <resourceGroup> -w <webAppName> -r <acrName> [-p <projectPath>] [-t <tag>]" >&2
}

RG=""; APP=""; ACR=""; PROJECT="../../apps/webapp"; TAG=""; ENVFILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--resource-group) RG="$2"; shift 2;;
    -w|--web-app) APP="$2"; shift 2;;
    -r|--acr) ACR="$2"; shift 2;;
    -p|--project) PROJECT="$2"; shift 2;;
    -t|--tag) TAG="$2"; shift 2;;
    --env-file) ENVFILE="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done
[[ -z "$RG" || -z "$APP" || -z "$ACR" ]] && { usage; exit 1; }

if [[ -z "$TAG" ]]; then
  TAG=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)
fi
LOGIN_SERVER=$(az acr show -n "$ACR" --query loginServer -o tsv)
IMAGE="$LOGIN_SERVER/webapp:$TAG"

if grep -q '5173' "$PROJECT/Dockerfile"; then
  echo "[WARN] Dockerfile uses port 5173; consider switching to 80 for App Service." >&2
fi

docker build -t "$IMAGE" "$PROJECT"
az acr login -n "$ACR" >/dev/null
docker push "$IMAGE"
az webapp config container set -g "$RG" -n "$APP" --docker-custom-image-name "$IMAGE" --docker-registry-server-url https://$LOGIN_SERVER >/dev/null

if [[ -f "$ENVFILE" ]]; then
  MAPARGS=()
  while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    MAPARGS+=("$line")
  done < "$ENVFILE"
  if [[ ${#MAPARGS[@]} -gt 0 ]]; then
    az webapp config appsettings set -g "$RG" -n "$APP" --settings "${MAPARGS[@]}" >/dev/null
  fi
fi
az webapp restart -g "$RG" -n "$APP" >/dev/null
echo "Deployed WebApp image $IMAGE"
