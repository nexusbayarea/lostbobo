#!/bin/bash
set -e

echo "=== SimHPC Gateway Starting ==="
echo "Environment: ${ENVIRONMENT:-unknown}"

# ------------------------------------------------------------------
# Infisical Bootstrap — fetch secrets at runtime
# ------------------------------------------------------------------
if [ -n "$INFISICAL_CLIENT_ID" ] && [ -n "$INFISICAL_CLIENT_SECRET" ]; then
    echo "Bootstrapping secrets from Infisical..."
    INFISICAL_TOKEN=$(curl -s -X POST https://app.infisical.com/api/v1/auth/universal-auth/login \
        -H "Content-Type: application/json" \
        -d "{\"clientId\": \"$INFISICAL_CLIENT_ID\", \"clientSecret\": \"$INFISICAL_CLIENT_SECRET\"}" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['accessToken'])" 2>/dev/null || echo "")

    if [ -z "$INFISICAL_TOKEN" ]; then
        echo "WARNING: Infisical auth failed. Using provided env vars."
    else
        SECRETS=$(curl -s -X GET \
            "https://app.infisical.com/api/v3/secrets/raw?environment=${INFISICAL_ENV:-production}&projectId=${INFISICAL_PROJECT_ID}" \
            -H "Authorization: Bearer $INFISICAL_TOKEN")

        echo "$SECRETS" | python3 -c "
import sys, json, os
data = json.load(sys.stdin)
for secret in data.get('secrets', []):
    key = secret['secretKey']
    value = secret['secretValue']
    os.environ[key] = value
" 2>/dev/null || echo "WARNING: Failed to parse secrets"
        echo "Infisical bootstrap complete."
    fi
fi

# ------------------------------------------------------------------
# Validate required secrets
# ------------------------------------------------------------------
REQUIRED="SUPABASE_URL SUPABASE_SERVICE_KEY JWT_SECRET DEEPSEEK_API_KEY"
MISSING=""
for var in $REQUIRED; do
    if [ -z "${!var}" ]; then
        MISSING="$MISSING $var"
    fi
done
if [ -n "$MISSING" ]; then
    echo "WARNING: Missing secrets:$MISSING"
fi

echo "=== Starting Gateway ==="
exec "$@"
