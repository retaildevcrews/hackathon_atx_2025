#!/usr/bin/env bash
set -euo pipefail

usage(){
  echo "Usage: $0 -u <uploadUrl> [-f <file>] [--context-type <type>] [--context-id <id>]" >&2
}

URL=""; FILE=""; CTX_TYPE="candidate"; CTX_ID="demo123"; SECRET="${SECRET:-}"; HEADER_SECRET=""; VERBOSE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -u|--url) URL="$2"; shift 2;;
    -f|--file) FILE="$2"; shift 2;;
    --context-type) CTX_TYPE="$2"; shift 2;;
    --context-id) CTX_ID="$2"; shift 2;;
    -s|--secret) SECRET="$2"; shift 2;;
    -v|--verbose) VERBOSE=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

[[ -z "$URL" ]] && { echo "Upload URL required" >&2; usage; exit 1; }

if [[ -n "$SECRET" ]]; then
  # Hash secret (sha256 hex) if caller passed raw secret vs hashed; allow 64-char hex passthrough
  if [[ ${#SECRET} -eq 64 && $SECRET =~ ^[0-9a-fA-F]+$ ]]; then
    HEADER_SECRET="$SECRET"
  else
    HEADER_SECRET=$(printf "%s" "$SECRET" | openssl dgst -sha256 | awk '{print $2}')
  fi
fi

tmpfile=""
if [[ -z "$FILE" ]]; then
  tmpfile=$(mktemp)
  head -c 128 /dev/urandom > "$tmpfile"
  FILE="$tmpfile"
fi


boundary="----hackathon$(date +%s%N)"
 
  # Use curl -F to build multipart form robustly (avoids manual boundary / printf pitfalls)
  curl_cmd=(curl -s -D - -o /dev/stdout -X POST "$URL" \
    -F "contextType=$CTX_TYPE" \
    -F "contextId=$CTX_ID" \
    -F "file=@$FILE;type=application/octet-stream")
  printf "\r\n--%s--\r\n" "$boundary"
  if [[ -n "$HEADER_SECRET" ]]; then
    curl_cmd+=( -H "x-internal-upload-key-sha256: $HEADER_SECRET" )
  fi
curl_args=(-s -D - -o /dev/stdout -X POST "$URL" \
  if [[ $VERBOSE -eq 1 ]]; then
    echo "[DEBUG] ${curl_cmd[*]}" >&2
  fi
  curl_args+=( -H "x-internal-upload-key-sha256: $HEADER_SECRET" )
  response=$("${curl_cmd[@]}" || true)

if [[ $VERBOSE -eq 1 ]]; then
  echo "[DEBUG] Curl command: curl ${curl_args[*]}" >&2
fi

response=$(curl "${curl_args[@]}" --data-binary @"$form") || true

# Split headers and body safely. Look for blank line separator.
headers=$(printf '%s' "$response" | awk 'NR==1,/^\r?$/')
body=$(printf '%s' "$response" | awk 'NR==1,/^\r?$/ {next} {print}')

# Extract last HTTP status line (handles interim 100 Continue)
  [[ -n "$tmpfile" ]] && rm -f "$tmpfile"
[ -z "$status" ] && status="000"

echo "HTTP Status: $status"
printf '%s\n' "$body"

rm -f "$form"
[[ -n "$tmpfile" ]] && rm -f "$tmpfile"

if [[ "$status" != "200" && "$status" != "201" ]]; then
  echo "Upload may have failed (status $status)" >&2
  exit 1
fi

echo "Smoke upload succeeded." >&2
