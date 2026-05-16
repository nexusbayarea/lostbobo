#!/bin/bash
set -e

echo "=== SimHPC Kernel Starting ==="
echo "Runtime Version: ${RUNTIME_VERSION:-unknown}"

if [ -n "$INFISICAL_CLIENT_ID" ] && [ -n "$INFISICAL_CLIENT_SECRET" ]; then
    echo "Bootstrapping secrets from Infisical..."
    export INFISICAL_TOKEN=$(curl -s -X POST https://app.infisical.com/api/v1/auth/universal-auth/login \
        -H "Content-Type: application/json" \
        -d "{\"clientId\": \"$INFISICAL_CLIENT_ID\", \"clientSecret\": \"$INFISICAL_CLIENT_SECRET\"}" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])")

    if [ -z "$INFISICAL_TOKEN" ]; then
        echo "ERROR: Failed to authenticate with Infisical"
        exit 1
    fi

    SECRETS=$(curl -s -X GET "https://app.infisical.com/api/v3/secrets/raw?environment=${INFISICAL_ENV:-production}&projectId=${INFISICAL_PROJECT_ID}" \
        -H "Authorization: Bearer $INFISICAL_TOKEN")

    echo "$SECRETS" | python3 -c "
import sys, json, os
secrets = json.load(sys.stdin)
for secret in secrets.get('secrets', []):
    key = secret['secretKey']
    value = secret['secretValue']
    os.environ[key] = value
    print(f'Loaded secret: {key}')
"
    echo "Infisical bootstrap complete."
else
    echo "Infisical credentials not provided. Using existing environment variables."
fi

REQUIRED_VARS="SUPABASE_URL SUPABASE_SERVICE_KEY JWT_SECRET"
for var in $REQUIRED_VARS; do
    if [ -z "${!var}" ]; then
        echo "ERROR: Required environment variable $var is not set"
        exit 1
    fi
done

if [ -f "$RUNTIME_MANIFEST" ]; then
    echo "Validating runtime manifest: $RUNTIME_MANIFEST"
    python3 -c "
import yaml, sys
with open('$RUNTIME_MANIFEST') as f:
    manifest = yaml.safe_load(f)
print(f'Manifest version: {manifest.get(\"manifest_version\", \"unknown\")}')
print(f'Components: {list(manifest.get(\"components\", {}).keys())}')
"
fi

echo "Verifying Supabase connectivity..."
python3 -c "
import os
from supabase import create_client
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
result = supabase.table('world_state_snapshots').select('snapshot_id').limit(1).execute()
print('Supabase connection verified.')
"

echo "=== Starting SimHPC Kernel ==="
exec "$@"
