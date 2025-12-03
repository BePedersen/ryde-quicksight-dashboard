# ryde-quicksight-dashboard

Selenium-basert applikasjon for fullskjerm-visning av AWS QuickSight-dashboards i kiosk-modus på Raspberry Pi og andre enheter.

## Features

- 🖥️ Fullskjerm visning av QuickSight dashboards
- 🔄 Automatisk reload hver 5. minutt (konfigurerbar)
- 🔐 Persistent login med lagret profil
- �� Støtter 46+ byer med dynamisk byvalg
- 🎨 Tema-bytte basert på tid (light 06:30-22:30, midnight 22:30-06:30)
- ⏰ Automatisk daglig restart (06:30, 14:30, 22:30)
- 📱 Optimalisert for Raspberry Pi

## Krav

### macOS
- Google Chrome (installert)
- Python 3.7+

### Raspberry Pi OS
```bash
sudo apt-get install -y chromium chromium-driver python3 python3-pip
```

## Instalasjon

### 1. Clone repositoriet
```bash
git clone https://github.com/BePedersen/ryde-quicksight-dashboard.git
cd ryde-quicksight-dashboard
```

### 2. Opprett `.env` fil
```bash
cp .env.sample .env
nano .env
```

### 3. Installer Python-pakker
Scriptet installerer automatisk nødvendige pakker (`selenium`, `python-dotenv`) ved første kjøring.

## Konfigurasjon

Redigér `.env` filen:

```ini
# Dashboard-modus: "operations" eller "mechanics"
DASHBOARD_MODE=operations

# Tema (valgfritt): "light" eller "midnight"
# Hvis ikke satt: automatisk bytte basert på tid
# THEME=light

# By (se .env.sample for full liste)
CITY=turku

# Refresh-intervall i sekunder
REFRESH_SECS=300

# Login-detaljer
USERNAME=brukernavn@domene.no
PASSWORD=passord
```

## Bruk

### Enkel kjøring
```bash
./scrape_quicksight.py
```

### Med systemctl (Raspberry Pi - auto-start ved boot)
```bash
# Installer service
sudo cp quicksight.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quicksight
sudo systemctl start quicksight

# Sjekk status
sudo systemctl status quicksight

# Se logger
journalctl -u quicksight -f
```

## Web Dashboard - Dashboard Manager

En web-basert dashboard for å administrere alle Raspberry Pi-ene sentralisert.

### Installasjon (Mac/Desktop)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend kjører på `http://localhost:5000`

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Frontend kjører på `http://localhost:5173`

Eller bygg for produksjon:
```bash
cd frontend
npm install
npm run build
python ../backend/app.py
```

Så besøk `http://localhost:5000`

### Funksjoner

- 📊 Dashboard med oversikt over alle 10 Pi-er
- ⚙️ Rediger CITY og DASHBOARD_MODE for hver Pi
- 🔄 Restart service fra web-UI
- 🔗 SSH-basert fjernkontroll (krever SSH-nøkler)

### Setup av SSH-nøkler (en gang per Pi)

**På Mac (genererer nøkkel):**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/ryde_pi -N ""
```

**Kopier til hver Pi (erstatt IP-adressen):**
```bash
ssh-copy-id -i ~/.ssh/ryde_pi.pub pi@192.168.1.101
ssh-copy-id -i ~/.ssh/ryde_pi.pub pi@192.168.1.102
# ... osv for alle 10 Pi-er
```

## Raspberry Pi 5 - Auto-start ved reboot

### Installasjon på Raspberry Pi

```bash
# Clone repo
git clone https://github.com/BePedersen/ryde-quicksight-dashboard.git /home/pi/quicksight
cd /home/pi/quicksight

# Opprett .env
cp .env.sample .env
nano .env  # Rediger CITY for denne Pi-en

# Installer pakker
pip install -r requirements.txt

# Lag systemctl service
sudo bash -c 'cat > /etc/systemd/system/quicksight.service << EOF
[Unit]
Description=AWS QuickSight Dashboard Display
After=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/quicksight
ExecStart=/usr/bin/python3 /home/pi/quicksight/scrape_quicksight.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
'

# Enable og start service
sudo systemctl daemon-reload
sudo systemctl enable quicksight
sudo systemctl start quicksight

# Sjekk at det kjører
sudo systemctl status quicksight
```

### Raspberry Pi 5 spesifikk - Hent SSH-nøkkel fra Mac

```bash
# På Pi - motta Mac sin public key
mkdir -p /home/pi/.ssh
chmod 700 /home/pi/.ssh

# Kopier fra Mac (kjør på Mac):
ssh-copy-id -i ~/.ssh/ryde_pi.pub pi@192.168.1.101
```

### Vedlikehold

```bash
# Se status
sudo systemctl status quicksight

# Se live logs
sudo journalctl -u quicksight -f

# Restart
sudo systemctl restart quicksight

# Stopp
sudo systemctl stop quicksight

# Start
sudo systemctl start quicksight
```

## Støttede Byer

Tilgjengelige byvalg i `CITY`:
asker, bergen, bodø, borås, changzhou, drammen, eskilstuna, fredrikstad, göteborg, halmstad, helsingborg, hämeenlinna, helsinki, hq, joensuu, jyväskylä, karlstad, kristiansand, kuopio, lahti, lappeenranta, linköping, luleå, malmö, moss, norrköping, not used, oslo, oulu, östersund, örebro, pori, sandefjord, seinäjoki, shanghai, skien, stavanger, sundsvall, tampere, trondheim, tromsø, turku, umeå, uppsala, vaasa, västeräs, växjö

## Tema-bytte

- **Automatisk (standard):** Light mode 06:30-22:30, midnight mode 22:30-06:30
- **Manuell:** Sett `THEME=light` eller `THEME=midnight` i `.env` for å låse til ett tema

## Vedlikehold på flere Raspberry Pi-er

### Oppdater kode på alle Pi-er
```bash
./update-all-pis.sh
```

### Sjekk status på alle Pi-er
```bash
./status-all-pis.sh
```

Se `PI_CONFIG.txt` for konfigurasjon av hver Pi.

## Feilsøking

### Ingen innlogging
- Sjekk `USERNAME` og `PASSWORD` i `.env`
- Sjekk at Chrome/Chromium er installert
- Se logs med: `sudo journalctl -u quicksight -f`

### Feil tema eller by
- Sjekk at `CITY` og `THEME` er stavd riktig (små bokstaver)
- Restart service: `sudo systemctl restart quicksight`

### Performance
- Øk `REFRESH_SECS` hvis Pi-en er treg
- Sjekk Chrome cache: `rm -rf /tmp/qschrome-profile` (fjerner lagret profil)

## Lisens

MIT

## Kontakt

benjamin.pedersen@ryde-technology.com
