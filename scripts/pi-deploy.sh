#!/usr/bin/env bash
set -e

INSTALL_DIR="${1:-$HOME/BUDGET_CALLY}"
SERVICE_NAME="${2:-budget_cally}"

cd "$INSTALL_DIR"

if [ ! -d .git ]; then
  echo "Error: no git repository found in ${INSTALL_DIR}. Please clone the repository first."
  exit 1
fi

git fetch --all
git reset --hard origin/main
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
sudo systemctl restart ${SERVICE_NAME}.service

echo "Deployment complete."
