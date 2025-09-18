#!/usr/bin/env bash
set -euo pipefail

usage(){
  echo "Usage: $0 -g <resourceGroup> -f <functionAppName> [-p <projectPath>] [--bypass]" >&2
}

RG=""; FUNC=""; PROJECT="../../apps/functions"; ZIP="function.zip"; BYPASS=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--resource-group) RG="$2"; shift 2;;
    -f|--function-app) FUNC="$2"; shift 2;;
    -p|--project) PROJECT="$2"; shift 2;;
    --bypass) BYPASS=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

[[ -z "$RG" || -z "$FUNC" ]] && { usage; exit 1; }

TMP=$(mktemp -d)
cp -R "$PROJECT"/* "$TMP"/
find "$TMP" -name '__pycache__' -type d -prune -exec rm -rf {} +
rm -f "$TMP"/Dockerfile 2>/dev/null || true
rm -f "$ZIP" || true
echo "[INFO] Packaging function app..."
if ! command -v zip >/dev/null 2>&1; then
  echo "[ERROR] 'zip' command not found. Please install zip (e.g. pacman -S zip in Git Bash / brew install zip / apt install zip)." >&2
  exit 1
fi
(cd "$TMP" && zip -r "$OLDPWD/$ZIP" . > /dev/null)
if [[ ! -f "$ZIP" ]]; then
  echo "[ERROR] Expected archive not found at $ZIP after packaging." >&2
  ls -al . >&2 || true
  exit 1
fi
echo "[INFO] Package created: $ZIP (size: $(stat -c%s "$ZIP" 2>/dev/null || stat -f%z "$ZIP" 2>/dev/null) bytes)"

# Retry wrapper for zip deploy (SCM warm-up can cause transient JSON decode errors)
MAX_ATTEMPTS=${MAX_ATTEMPTS:-6}
INITIAL_DELAY=${INITIAL_DELAY:-5}
attempt=1
delay=$INITIAL_DELAY
while true; do
  echo "[INFO] Deploying zip (attempt $attempt/$MAX_ATTEMPTS)..."
  set +e
  output=$(az functionapp deployment source config-zip -g "$RG" -n "$FUNC" --src "$PWD/$ZIP" 2>&1)
  status=$?
  set -e
  if [[ $status -eq 0 ]]; then
    echo "[INFO] Zip deploy succeeded on attempt $attempt."; break
  fi

  # Detect 401 in output and attempt manual zipdeploy fallback using publishing profile
  if echo "$output" | grep -qi "401"; then
    echo "[WARN] Received 401 from config-zip. Attempting manual zipdeploy fallback..." >&2
    pub_xml=$(az webapp deployment list-publishing-profiles -g "$RG" -n "$FUNC" --xml 2>/dev/null || true)
    if [[ -z "$pub_xml" ]]; then
      echo "[ERROR] Could not obtain publishing profile for manual fallback." >&2
    else
      # Extract username & password (first profile) from XML. Using grep/sed - crude but avoids external deps.
      user=$(echo "$pub_xml" | sed -n 's/.*userName="\([^"]*\)".*/\1/p' | head -n1)
      pass=$(echo "$pub_xml" | sed -n 's/.*userPWD="\([^"]*\)".*/\1/p' | head -n1)
      scmHost=$(echo "$pub_xml" | sed -n 's/.*publishUrl="\([^"]*\)".*/\1/p' | head -n1)
      if [[ -n "$user" && -n "$pass" && -n "$scmHost" ]]; then
        echo "[INFO] Performing direct POST to https://$scmHost/api/zipdeploy" >&2
        # Use basic auth with curl; -sS for concise errors
        set +e
        curl -sS -u "$user:$pass" -X POST "https://$scmHost/api/zipdeploy" --data-binary @"$ZIP" -H 'Content-Type: application/zip' > deployment.log 2>&1
        curl_status=$?
        set -e
        if [[ $curl_status -eq 0 ]]; then
          echo "[INFO] Manual zipdeploy fallback succeeded." >&2
          break
        else
          echo "[WARN] Manual zipdeploy fallback failed (curl exit $curl_status)." >&2
        fi
      else
        echo "[ERROR] Failed to parse publishing profile credentials for fallback." >&2
      fi
    fi
  fi

  echo "[WARN] Zip deploy failed (attempt $attempt): $output" >&2
  if (( attempt >= MAX_ATTEMPTS )); then
    echo "[ERROR] Zip deploy failed after $MAX_ATTEMPTS attempts (including fallback)." >&2
    exit 1
  fi
  echo "[INFO] Waiting $delay seconds before retry..."; sleep $delay
  attempt=$((attempt+1))
  delay=$((delay*2))
done
if [[ $BYPASS -eq 1 ]]; then
  az functionapp config appsettings set -g "$RG" -n "$FUNC" --settings DISABLE_INTERNAL_UPLOAD_AUTH=true >/dev/null
fi
echo "Deployed function zip to $FUNC"
rm -rf "$TMP"
