#!/bin/bash
# =============================================================================
# SimHPC VPS Bootstrap — idempotent, safe to re-run
# Run once on a bare Ubuntu 24.04 DigitalOcean droplet.
# Usage: bash setup-vps.sh
# =============================================================================
set -euo pipefail

echo "=== SimHPC VPS Bootstrap ==="

# Configuration — customize these
REPO_URL="${REPO_URL:-https://github.com/YOUR_ORG/simhpc-gamma.git}"
MOUNT_POINT="/mnt/simhpc_vps"
VOLUME_ID="scsi-0DO_Volume_simhpc-vps"

# ------------------------------------------------------------------
# 1. Install Docker
# ------------------------------------------------------------------
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "Docker already installed: $(docker --version)"
fi

if ! command -v docker compose &>/dev/null; then
    echo "Installing Docker Compose plugin..."
    apt-get update
    apt-get install -y docker-compose-plugin
fi

# ------------------------------------------------------------------
# 2. Install system dependencies
# ------------------------------------------------------------------
apt-get update
apt-get install -y --no-install-recommends \
    git \
    curl \
    python3 \
    python3-pip

# ------------------------------------------------------------------
# 3. Mount persistent volume
# ------------------------------------------------------------------
if [ -L "/dev/disk/by-id/$VOLUME_ID" ]; then
    if ! grep -q "$MOUNT_POINT" /etc/fstab 2>/dev/null; then
        echo "Formatting and mounting persistent volume..."
        mkfs.ext4 -F "/dev/disk/by-id/$VOLUME_ID"
        mkdir -p "$MOUNT_POINT"
        mount -o discard,defaults,noatime "/dev/disk/by-id/$VOLUME_ID" "$MOUNT_POINT"
        echo "/dev/disk/by-id/$VOLUME_ID $MOUNT_POINT ext4 defaults,nofail,discard 0 0" >> /etc/fstab
    else
        echo "Volume already mounted at $MOUNT_POINT"
        mount -a
    fi

    echo "Creating subdirectories..."
    mkdir -p "$MOUNT_POINT"/{logs,documents,graph,uploads,simulations,cache}
else
    echo "WARNING: Volume $VOLUME_ID not found. Skipping mount."
fi

# ------------------------------------------------------------------
# 4. Clone repository
# ------------------------------------------------------------------
if [ ! -d "$MOUNT_POINT/simhpc-gamma" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$MOUNT_POINT/simhpc-gamma"
else
    echo "Repository already cloned. Pulling latest..."
    cd "$MOUNT_POINT/simhpc-gamma"
    git pull
fi

cd "$MOUNT_POINT/simhpc-gamma"

# ------------------------------------------------------------------
# 5. Configure UFW firewall
# ------------------------------------------------------------------
echo "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 8080/tcp comment 'SimHPC Gateway'
ufw --force enable
echo "Firewall: port 22 (SSH) and 8080 (gateway) open."

# ------------------------------------------------------------------
# 6. Print next steps
# ------------------------------------------------------------------
echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "Next steps:"
echo ""
echo "  1. Set Infisical credentials:"
echo "     export INFISICAL_CLIENT_ID=\"your-client-id\""
echo "     export INFISICAL_CLIENT_SECRET=\"your-client-secret\""
echo "     export INFISICAL_PROJECT_ID=\"your-project-id\""
echo "     export INFISICAL_ENV=\"production\""
echo ""
echo "  2. Or set secrets directly for testing:"
echo "     export SUPABASE_URL=\"https://your-project.supabase.co\""
echo "     export SUPABASE_SERVICE_KEY=\"your-key\""
echo "     export DEEPSEEK_API_KEY=\"your-key\""
echo "     export JWT_SECRET=\"your-secret\""
echo ""
echo "  3. Start services:"
echo "     cd $MOUNT_POINT/simhpc-gamma"
echo "     docker compose -f deployment/docker-compose.yml up -d"
echo ""
echo "  4. Validate:"
echo "     bash deployment/scripts/validate-cpu.sh"
