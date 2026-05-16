#!/bin/bash
set -e

echo "=== Infisical Bootstrap ==="

if ! command -v infisical &> /dev/null; then
    echo "Installing Infisical CLI..."
    curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash
    sudo apt-get update && sudo apt-get install -y infisical
fi

infisical login

infisical export --env production --format dotenv > .env.infisical

echo "Secrets written to .env.infisical"
echo "Add to .gitignore - NEVER commit this file."
