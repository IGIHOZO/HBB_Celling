#!/usr/bin/env bash
# ============================================================================
# Sync Oracle HBB Customers -> PostgreSQL hbb_customers
# ============================================================================
# This script fetches the latest Home-Broadband / HBB subscribers from
# Oracle (PCRF) and imports them into the PostgreSQL hbb_customers table.
#
# Requirements (will be checked):
#   - python3
#   - oracledb  (pip install oracledb)
#   - psycopg2 (pip install psycopg2-binary)
#
# Usage:
#   ./sync_oracle_to_postgres.sh           # full sync
#   ./sync_oracle_to_postgres.sh --dry-run # count only
#   ./sync_oracle_to_postgres.sh --env /path/to/.env
#
# Cron example (daily at 02:00):
#   0 2 * * * cd /opt/hbb && ./scripts/sync_oracle_to_postgres.sh >> /var/log/hbb_sync.log 2>&1
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_DIR}/.env"
PYTHON="${PYTHON:-python3}"
DRY_RUN=""

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --env)
            ENV_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--env /path/to/.env]"
            echo ""
            echo "  --dry-run   Count Oracle records only, do not import"
            echo "  --env       Path to .env file (default: ${PROJECT_DIR}/.env)"
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown option: $1"
            echo "Run '$0 --help' for usage."
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
echo "========================================"
echo "  HBB Oracle -> PostgreSQL Sync"
echo "========================================"
echo ""

# Check .env exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "[ERROR] .env file not found: $ENV_FILE"
    exit 1
fi
echo "[OK] .env file found: $ENV_FILE"

# Check python3
if ! command -v "$PYTHON" &>/dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH."
    exit 1
fi
echo "[OK] Python: $($PYTHON --version)"

# Check required Python packages
REQUIRED_PKGS=("oracledb" "psycopg2")
MISSING_PKGS=()
for pkg in "${REQUIRED_PKGS[@]}"; do
    if ! $PYTHON -c "import ${pkg}" 2>/dev/null; then
        MISSING_PKGS+=("$pkg")
    fi
done

if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
    echo ""
    echo "[ERROR] Missing Python packages: ${MISSING_PKGS[*]}"
    echo ""
    echo "Install them with:"
    echo "  pip install oracledb psycopg2-binary"
    echo ""
    echo "Or activate the project virtualenv:"
    if [[ -d "${PROJECT_DIR}/.venv" ]]; then
        echo "  source ${PROJECT_DIR}/.venv/bin/activate"
    fi
    exit 1
fi
echo "[OK] Required Python packages installed."

# ---------------------------------------------------------------------------
# Run the sync
# ---------------------------------------------------------------------------
echo ""
echo "[START] Running sync script ..."
echo ""

$PYTHON "$SCRIPT_DIR/sync_oracle_hbb.py" \
    --env "$ENV_FILE" \
    ${DRY_RUN}

SYNC_EXIT=$?

echo ""
if [[ $SYNC_EXIT -eq 0 ]]; then
    echo "[SUCCESS] Sync completed."
else
    echo "[FAILURE] Sync exited with code $SYNC_EXIT."
    exit $SYNC_EXIT
fi
