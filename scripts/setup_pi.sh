#!/usr/bin/env bash
set -e

INSTALL_DIR="${1:-$HOME/BUDGET_CALLY}"
SERVICE_NAME="${2:-budget_cally}"

echo "Setting up Budget Cally in ${INSTALL_DIR}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d .git ]; then
  echo "Error: no git repository found in ${INSTALL_DIR}. Please clone the repo first."
  exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Budget Cally Flask App
After=network.target

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl restart ${SERVICE_NAME}.service

echo "Setup complete."
