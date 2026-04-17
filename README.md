# Budget Cally

A simple Flask budget tracker.

## Raspberry Pi deployment

This repo now includes a Pi-friendly deployment setup with a systemd service and optional GitHub Actions deployment.

### 1. First-time Pi setup

On your Raspberry Pi:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

Clone the repo into a directory such as `~/BUDGET_CALLY`:

```bash
git clone <your-repo-url> ~/BUDGET_CALLY
cd ~/BUDGET_CALLY
chmod +x scripts/setup_pi.sh scripts/pi-deploy.sh
```

Run the setup script:

```bash
sudo ./scripts/setup_pi.sh ~/BUDGET_CALLY
```

This will:
- create and activate a Python virtual environment
- install `requirements.txt`
- create a `systemd` service named `budget_cally.service`
- enable and start the service

### 2. Manual updates on the Pi

When you want to update the site manually on the Pi:

```bash
cd ~/BUDGET_CALLY
./scripts/pi-deploy.sh ~/BUDGET_CALLY
```

### 3. Automated deploys via GitHub Actions

If you want CI/CD, add these secrets to your GitHub repository:

- `PI_HOST` — Raspberry Pi IP or hostname
- `PI_USER` — SSH username (e.g. `pi`)
- `PI_SSH_KEY` — private SSH key with access to the Pi
- `PI_PORT` — optional SSH port (default `22`)

Push to the `main` branch and the workflow in `.github/workflows/deploy.yml` will copy the project to your Pi, install dependencies, and restart the service.

> Note: the Pi user should be able to run `sudo systemctl restart budget_cally.service` without a password, or you can adjust the workflow to use a passwordless sudo setup.

### 4. Troubleshooting

Check service logs on the Pi:

```bash
sudo journalctl -u budget_cally.service -f
```

Restart the service manually if needed:

```bash
sudo systemctl restart budget_cally.service
```

### 5. Notes

- This setup keeps your code on GitHub and deploys changes to the Pi from `main`.
- If you prefer, you can skip GitHub Actions and just use `git pull` + `./scripts/pi-deploy.sh` on the Pi.
