#!/usr/bin/env bash
set -e

# Projektverzeichnis: über Argument oder aktuelles Verzeichnis
PROJECT_DIR="${1:-$(pwd)}"

# Überprüfen, ob die nötigen Dateien existieren
if [ ! -f "$PROJECT_DIR/client.py" ]; then
  echo "Fehler: client.py nicht gefunden in $PROJECT_DIR"
  exit 1
fi
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "Fehler: requirements.txt nicht gefunden in $PROJECT_DIR"
  exit 1
fi

# Bestimmen des Users für den Service
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
  RUN_USER="$SUDO_USER"
else
  RUN_USER=$(stat -c '%U' "$PROJECT_DIR")
fi

echo "-> Projektverzeichnis: $PROJECT_DIR"
echo "-> Service-User: $RUN_USER"

# Virtuelle Umgebung erstellen und Abhängigkeiten installieren
python3 -m venv "$PROJECT_DIR/env"
# Aktivieren der venv (POSIX-kompatibel)
. "$PROJECT_DIR/env/bin/activate"
# pip aktualisieren und Abhängigkeiten installieren
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"
deactivate

# systemd-Service-Datei schreiben
SERVICE_FILE="/etc/systemd/system/zeitanzeige.service"
echo "-> Erstelle/aktualisiere Service: $SERVICE_FILE"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=My Tkinter App
After=network.target

[Service]
User=$RUN_USER
Environment=DISPLAY=:0
ExecStart=$PROJECT_DIR/env/bin/python3 $PROJECT_DIR/client.py
WorkingDirectory=$PROJECT_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
EOF

# systemd neu laden, aktivieren und Service starten
sudo systemctl daemon-reload
sudo systemctl enable zeitanzeige.service
sudo systemctl restart zeitanzeige.service

echo "-> Setup abgeschlossen. Raspberry Pi wird neu gestartet."
sudo reboot
